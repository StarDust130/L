from workers.ingestion.discovery import discover_job_links
from workers.ingestion.extract import dedupe_key, extract_job
from workers.ingestion.quality import evaluate_job
from workers.ingestion.sources import SOURCES


def test_has_exactly_ten_sources():
    assert len(SOURCES) == 10


def test_discovery_filters_to_source_domain():
    profile = SOURCES[0]
    html = '''<a href="https://www.ycombinator.com/jobs/123">Software Engineer</a><a href="https://evil.com/job/1">bad</a>'''
    found = discover_job_links(html, profile.listing_urls[0], profile)
    assert len(found) == 1
    assert "ycombinator.com" in found[0].url


def test_jsonld_job_extraction():
    html = '''<html><head><script type="application/ld+json">{"@type":"JobPosting","title":"Full Stack Engineer","hiringOrganization":{"name":"Acme"},"jobLocation":{"address":{"addressLocality":"Bengaluru","addressCountry":"IN"}},"datePosted":"2026-09-01"}</script></head><body></body></html>'''
    job = extract_job(html, "https://example.com/jobs/1")
    assert job is not None
    assert job.title == "Full Stack Engineer"
    assert job.company_name == "Acme"
    assert dedupe_key(job)


def test_india_job_is_accepted():
    html = '''<script type="application/ld+json">{"@type":"JobPosting","title":"Backend Engineer","hiringOrganization":{"name":"Acme"},"jobLocation":{"address":{"addressLocality":"Bengaluru","addressCountry":"IN"}},"description":"Backend role. Responsibilities and requirements. Apply now."}</script>'''
    job = extract_job(html, "https://example.com/jobs/2")
    decision = evaluate_job(job)
    assert decision.accepted
    assert decision.category == "tech"


def test_us_only_remote_is_rejected():
    html = '''<script type="application/ld+json">{"@type":"JobPosting","title":"Software Engineer","hiringOrganization":{"name":"Acme"},"jobLocationType":"TELECOMMUTE","applicantLocationRequirements":{"@type":"Country","name":"United States"},"description":"US only remote role. Requirements and responsibilities."}</script>'''
    job = extract_job(html, "https://example.com/jobs/3")
    decision = evaluate_job(job)
    assert not decision.accepted
