from pydantic import BaseModel, Field


class SearchQueries(BaseModel):
    queries: list[str] = Field(default_factory = list, description = "List of search queries to find relevant news articles. Each query should be a concise phrase or keyword related to the user's interests or specified topics. The queries will be used to retrieve news articles from various sources, so they should be specific enough to yield relevant results while broad enough to capture a range of related articles.")

class ScoreOutput(BaseModel):
    analysis: str = Field(
        description="A brief analysis of how the article content relates to the user's specific interests."
    )
    score: int = Field(
        description="A relevance score on a scale of 1 to 10."
    )