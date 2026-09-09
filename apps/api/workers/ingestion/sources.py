from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceProfile:
    key: str
    name: str
    domain: str
    source_type: str
    listing_urls: tuple[str, ...]
    include_url_terms: tuple[str, ...] = ()
    exclude_url_terms: tuple[str, ...] = ()
    max_listing_pages: int = 2
    max_job_urls_per_page: int = 40
    requires_browser: bool = False
    notes: str = ""
    job_link_hints: tuple[str, ...] = (
        "/job", "/jobs/", "/career", "/careers/", "/positions/", "/openings/", "/vacancy/"
    )
    allowed_remote_scopes: tuple[str, ...] = ("india", "worldwide")
    extra_headers: dict[str, str] = field(default_factory=dict)


# V1 deliberately uses only 10 sources. These are source profiles, not ten scrapers.
# URLs are starting points; the generic engine discovers individual job links from them.
SOURCES: tuple[SourceProfile, ...] = (
    SourceProfile(
        key="yc_jobs",
        name="Y Combinator Jobs",
        domain="ycombinator.com",
        source_type="startup_jobs",
        listing_urls=("https://www.ycombinator.com/jobs", "https://www.ycombinator.com/companies"),
        include_url_terms=("/jobs", "/companies"),
        exclude_url_terms=("/companies/", "/people/", "/events/"),
        notes="YC has startup/company discovery and job pages. Prefer actual job URLs; company pages are a discovery path.",
    ),
    SourceProfile(
        key="wellfound",
        name="Wellfound",
        domain="wellfound.com",
        source_type="startup_jobs",
        listing_urls=("https://wellfound.com/jobs", "https://wellfound.com/remote"),
        include_url_terms=("/jobs", "/job/", "/role/"),
        exclude_url_terms=("/companies/", "/people/"),
        notes="Startup-heavy source; remote pages need eligibility verification rather than assuming worldwide.",
    ),
    SourceProfile(
        key="cutshort",
        name="Cutshort",
        domain="cutshort.io",
        source_type="india_jobs",
        listing_urls=("https://cutshort.io/jobs",),
        include_url_terms=("/job", "/jobs"),
        exclude_url_terms=("/companies/", "/blog/"),
        notes="India-focused technology/startup hiring source.",
    ),
    SourceProfile(
        key="instahyre",
        name="Instahyre",
        domain="instahyre.com",
        source_type="india_jobs",
        listing_urls=("https://www.instahyre.com/search-jobs/",),
        include_url_terms=("/job", "/search-jobs"),
        exclude_url_terms=("/blog/", "/companies/"),
        notes="India hiring source; browser fallback is expected if listings are JS-rendered.",
    ),
    SourceProfile(
        key="himalayas",
        name="Himalayas",
        domain="himalayas.app",
        source_type="remote_jobs",
        listing_urls=("https://himalayas.app/jobs",),
        include_url_terms=("/jobs", "/job/"),
        exclude_url_terms=("/companies/", "/guides/"),
        notes="Remote-first source. Treat remote geography as explicit data, not an assumption.",
    ),
    SourceProfile(
        key="weworkremotely",
        name="We Work Remotely",
        domain="weworkremotely.com",
        source_type="remote_jobs",
        listing_urls=("https://weworkremotely.com/remote-jobs",),
        include_url_terms=("/remote-jobs/",),
        exclude_url_terms=("/categories/", "/companies/", "/guides/"),
        notes="Remote job board; verify country restrictions from each job.",
    ),
    SourceProfile(
        key="remoteok",
        name="Remote OK",
        domain="remoteok.com",
        source_type="remote_jobs",
        listing_urls=("https://remoteok.com/",),
        include_url_terms=("/remote-jobs/", "/remote-"),
        exclude_url_terms=("/api/", "/blog/"),
        notes="Remote-heavy source. Structured data may be easier than visual scraping.",
    ),
    SourceProfile(
        key="remotive",
        name="Remotive",
        domain="remotive.com",
        source_type="remote_jobs",
        listing_urls=("https://remotive.com/remote-jobs",),
        include_url_terms=("/remote-jobs/",),
        exclude_url_terms=("/remote-jobs/category/", "/blog/"),
        notes="Remote-focused source with structured job information on many pages.",
    ),
    SourceProfile(
        key="naukri",
        name="Naukri",
        domain="naukri.com",
        source_type="india_jobs",
        listing_urls=("https://www.naukri.com/jobs-in-india",),
        include_url_terms=("/job-listings-", "/jobs/", "-jobs-"),
        exclude_url_terms=("/mnjuser/", "/blog/", "/companies/"),
        notes="Large India job source; use browser only when normal HTTP/structured extraction cannot work.",
    ),
    SourceProfile(
        key="indeed_india",
        name="Indeed India",
        domain="in.indeed.com",
        source_type="india_jobs",
        listing_urls=("https://in.indeed.com/jobs",),
        include_url_terms=("/viewjob", "/rc/clk", "/jobs"),
        exclude_url_terms=("/companies/", "/career-advice/"),
        notes="Large India source; respect robots/access controls and treat browser as fallback only.",
    ),
)


def get_source_profiles() -> tuple[SourceProfile, ...]:
    return SOURCES
