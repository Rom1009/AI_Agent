from typing import Annotated, TypedDict, List

class DigestState(TypedDict):
    user_id: str
    run_date: str
    topics: list[str]
    max_articles_per_topic: int
    output_language: str
    digest_style: str
    user_interests: list[str]
    src_url: list[str]

    queries: list[str]
    candidate_urls: list[dict]
    fetched_docs: list[dict]
    filtered_docs: list[dict]
    filtered_aricles: list[dict]
    summarized_docs: list[dict]

    email_subject: str
    email_markdown: str
    email_html: str
    warnings: list[str]