import logging
from dataclasses import dataclass
from urllib.parse import urlsplit

from sqlalchemy.ext.asyncio import AsyncSession

from .browser import BrowserFetcher
from .discovery import CandidateURL, discover_job_links
from .extract import extract_job
from .http import HttpFetcher
from .llm import SemanticJobJudge
from .quality import evaluate_job
from .repository import ensure_source, save_job, start_run
from .sources import SourceProfile, get_source_profiles

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestionStats:
    source: str
    listing_pages: int = 0
    candidate_urls: int = 0
    jobs_extracted: int = 0
    jobs_saved: int = 0
    jobs_rejected: int = 0
    errors: int = 0


class IngestionWorker:
    """Isolated Worker 2. Worker 1/3/Agent do not belong here."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        http: HttpFetcher | None = None,
        browser: BrowserFetcher | None = None,
        semantic_judge: SemanticJobJudge | None = None,
    ) -> None:
        self.session = session
        self.http = http or HttpFetcher()
        self.browser = browser or BrowserFetcher()
        self.semantic_judge = semantic_judge or SemanticJobJudge()

    async def _fetch(self, profile: SourceProfile, url: str) -> tuple[str, str]:
        """Return (html, method). Never tries to bypass access controls."""
        if not profile.requires_browser:
            try:
                page = await self.http.fetch(url, headers=profile.extra_headers)
                if "text/html" in page.content_type or "application/xhtml+xml" in page.content_type:
                    return page.html, "http"
            except Exception as exc:
                logger.info("HTTP fetch failed for %s: %s", url, exc)

        page = await self.browser.fetch(url)
        return page.html, "browser"

    async def run_source(self, profile: SourceProfile) -> IngestionStats:
        source = await ensure_source(self.session, profile)
        run = await start_run(self.session, profile)
        stats = IngestionStats(source=profile.key)
        listing_pages = 0
        candidate_urls: list[CandidateURL] = []

        try:
            for listing_url in profile.listing_urls[: profile.max_listing_pages]:
                try:
                    html, method = await self._fetch(profile, listing_url)
                    listing_pages += 1
                    discovered = discover_job_links(html, listing_url, profile)
                    candidate_urls.extend(discovered)
                    logger.info("%s: %s candidates from %s via %s", profile.name, len(discovered), listing_url, method)
                except Exception as exc:
                    logger.warning("%s listing failed: %s", profile.name, exc)

            # URL-level dedupe before expensive page fetches.
            unique: dict[str, CandidateURL] = {}
            for candidate in candidate_urls:
                unique.setdefault(candidate.url, candidate)

            extracted_count = saved_count = rejected_count = errors = 0
            for candidate in list(unique.values())[: profile.max_job_urls_per_page * max(1, profile.max_listing_pages)]:
                try:
                    html, method = await self._fetch(profile, candidate.url)
                    job = extract_job(html, candidate.url, candidate.title)
                    if not job:
                        rejected_count += 1
                        continue

                    # LLM is a bounded fallback only when deterministic extraction is ambiguous.
                    # The normal high-confidence JSON-LD path never needs it.
                    if job.extraction_confidence < 0.75:
                        patch = await self.semantic_judge.judge(
                            title=job.title,
                            text=job.description or "",
                        )
                        if patch and patch.confidence >= 0.75:
                            from dataclasses import replace
                            job = replace(
                                job,
                                company_name=patch.company_name or job.company_name,
                                location_text=patch.location_text or job.location_text,
                                remote_scope=patch.remote_scope,
                                extraction_confidence=max(job.extraction_confidence, patch.confidence),
                                method=f"{job.method}+llm",
                                evidence={**job.evidence, "llm_verified": True},
                            )
                    extracted_count += 1
                    decision = evaluate_job(job)
                    if not decision.accepted:
                        rejected_count += 1
                        continue
                    if await save_job(self.session, profile, job, decision):
                        saved_count += 1
                except Exception as exc:
                    errors += 1
                    logger.warning("%s job failed %s: %s", profile.name, candidate.url, exc)

            run.listing_pages = listing_pages
            run.candidate_urls = len(unique)
            run.jobs_extracted = extracted_count
            run.jobs_saved = saved_count
            run.jobs_rejected = rejected_count
            run.errors = errors
            run.status = "completed" if errors == 0 or extracted_count > 0 else "partial"
            source.last_run_at = run.started_at
            source.last_success_at = source.last_run_at if extracted_count else source.last_success_at
            source.consecutive_failures = 0 if extracted_count else source.consecutive_failures + 1
            source.jobs_seen_total += extracted_count
            source.jobs_saved_total += saved_count
            source.health_score = max(0.0, min(1.0, 1.0 - source.consecutive_failures * 0.2))
            source.last_error = None if extracted_count else "No extractable jobs found"
            await self.session.commit()
            return IngestionStats(profile.key, listing_pages, len(unique), extracted_count, saved_count, rejected_count, errors)
        except Exception as exc:
            await self.session.rollback()
            run.status = "failed"
            run.error_message = str(exc)[:2000]
            await self.session.commit()
            raise

    async def run(self, profiles: tuple[SourceProfile, ...] | None = None) -> list[IngestionStats]:
        profiles = profiles or get_source_profiles()
        results: list[IngestionStats] = []
        for profile in profiles:
            # Source isolation: one broken source must not stop the other 9.
            try:
                results.append(await self.run_source(profile))
            except Exception as exc:
                logger.exception("Source %s failed completely: %s", profile.key, exc)
                results.append(IngestionStats(profile.key, errors=1))
        return results
