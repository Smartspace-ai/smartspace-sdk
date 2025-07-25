from typing import Annotated, Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field
from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory

# Pydantic Models for the Google Custom Search API response


class SearchUrl(BaseModel):
    type: Optional[str] = Field(None, description="MIME type for the response format")
    template: Optional[str] = Field(None, description="URL template for API requests")


class QueryRequest(BaseModel):
    title: Optional[str] = Field(None, description="Title of the query request")
    totalResults: Optional[str] = Field(None, description="Total results returned")
    searchTerms: Optional[str] = Field(None, description="The search query string")
    count: Optional[int] = Field(None, description="Number of results per page")
    startIndex: Optional[int] = Field(
        None, description="The starting index for results"
    )
    inputEncoding: Optional[str] = Field(
        None, description="Input encoding for the query"
    )
    outputEncoding: Optional[str] = Field(
        None, description="Output encoding for the query"
    )
    safe: Optional[str] = Field(None, description="Safe search setting")
    cx: Optional[str] = Field(None, description="Custom search engine ID")


class Queries(BaseModel):
    request: List[QueryRequest] = Field(
        ..., description="Details of the current search query"
    )
    nextPage: Optional[List[QueryRequest]] = Field(
        None, description="Details to retrieve the next page of results"
    )


class SearchInformation(BaseModel):
    searchTime: Optional[float] = Field(
        None, description="Time taken for the search in seconds"
    )
    formattedSearchTime: Optional[str] = Field(
        None, description="Formatted search time"
    )
    totalResults: Optional[str] = Field(
        None, description="Total number of results as a string"
    )
    formattedTotalResults: Optional[str] = Field(
        None, description="Formatted total number of results"
    )


class SearchItem(BaseModel):
    kind: Optional[str] = Field(None, description="Type of the search result item")
    title: Optional[str] = Field(None, description="Title of the search result")
    htmlTitle: Optional[str] = Field(None, description="HTML formatted title")
    link: Optional[str] = Field(None, description="Direct URL to the search result")
    displayLink: Optional[str] = Field(None, description="Simplified display URL")
    snippet: Optional[str] = Field(None, description="Short snippet of the result")
    htmlSnippet: Optional[str] = Field(None, description="HTML formatted snippet")
    formattedUrl: Optional[str] = Field(None, description="User-friendly URL")
    htmlFormattedUrl: Optional[str] = Field(None, description="HTML formatted URL")
    pagemap: Optional[Dict[str, Any]] = Field(
        None, description="Additional structured data if available"
    )


class GoogleSearchResponse(BaseModel):
    kind: Optional[str] = Field(None, description="Response type")
    url: Optional[SearchUrl] = Field(
        None, description="URL details for the API response"
    )
    queries: Optional[Queries] = Field(None, description="Query metadata")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Additional context about the search"
    )
    searchInformation: Optional[SearchInformation] = Field(
        None, description="Performance information for the search"
    )
    items: Optional[List[SearchItem]] = Field(
        None, description="List of search result items"
    )


# Block implementation that uses the Pydantic models
@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    A block that connects to the Google Custom Search API, parses the JSON response 
    into a Pydantic model, and returns the structured result.
    It uses a configuration value 'page' (default=1) to determine which page of results to fetch.
    """,
    icon="fa-search",
)
class GoogleSearch(Block):
    google_api_key: Annotated[str, Config()]
    search_engine_id: Annotated[str, Config()]
    # New config value for the page number (defaults to 1)
    page: Annotated[int, Config()] = 1

    @step(output_name="search_results")
    async def run_search(
        self,
        query: Annotated[
            str,
            Metadata(description="The query string to search on Google"),
        ],
    ) -> GoogleSearchResponse:
        """
        Connects to the Google Custom Search API using the provided API key, search engine ID,
        and the configured page number (defaulting to 1). The method calculates the 'start'
        parameter based on the page number and returns the structured result as a Pydantic model.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        # Calculate the start index: page 1 -> start=1, page 2 -> start=11, etc.
        start_index = (self.page - 1) * 10 + 1
        params = {
            "key": self.google_api_key,
            "cx": self.search_engine_id,
            "q": query,
            "start": start_index,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
            response.raise_for_status()
            raw_json = response.json()
            # Use model_validate to convert the raw JSON into our Pydantic model
            parsed_response = GoogleSearchResponse.model_validate(raw_json)
            return parsed_response
        except httpx.HTTPError as e:
            raise ValueError(f"Error while connecting to Google Search API: {e}")
