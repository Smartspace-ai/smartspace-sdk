import asyncio
from collections import deque
from typing import Annotated, List, Set
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from smartspace.core import Block, Config, Output, metadata, step
from smartspace.enums import BlockCategory


class WebsiteDetails(BaseModel):
    title: str
    url: str
    content: str


@metadata(
    description="Scrapes the content of a website. Returns both the raw content and the content with metadata.",
    category=BlockCategory.MISC,
    icon="fa-globe",
)
class WebsiteScraper(Block):
    website_content: Output[list[str]]
    website_details: Output[list[WebsiteDetails]]
    page_limit: Annotated[int, Config()] = 3

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    @step()
    async def scrape_website(self, base_url: str):
        if not base_url:
            self.website_content.send([""])
            return

        if not urlparse(base_url).scheme:
            base_url = f"https://{base_url}"

        visited: Set[str] = set()
        pages_to_visit = deque([base_url])
        scraped_content: List[WebsiteDetails] = []

        async def fetch_page(url: str):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(url, headers=self.headers)
                    if response.status_code == 301:
                        url = response.headers["Location"]
                        response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    return response
            except httpx.HTTPError as e:
                print(f"Failed to fetch {url}: {e}")
                return None

        async def process_page(url: str):
            if url in visited:
                return

            response = await fetch_page(url)
            if not response:
                return

            visited.add(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the main content
            for script in soup(["script", "style"]):
                script.decompose()  # Remove unnecessary tags

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            text = "\n".join(line for line in lines if line)
            title = soup.title.string if soup.title and soup.title.string else ""
            scraped_content.append(WebsiteDetails(title=title, url=url, content=text))

            # Find and queue additional pages to visit
            for link_tag in soup.find_all("a", href=True):
                link = link_tag["href"]
                full_url = urljoin(base_url, link)
                # Stay within the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited and full_url not in pages_to_visit:
                        pages_to_visit.append(full_url)

        # process first page
        await process_page(base_url)
        tasks = []
        while (
            pages_to_visit
            # limit the number of pages to visit
            and len(visited) < self.page_limit
        ):
            url = pages_to_visit.popleft()
            if url not in visited:
                tasks.append(asyncio.create_task(process_page(url)))
            # run when we have 5 tasks or we have reached the page limit
            if (len(tasks) + len(visited) == self.page_limit) or len(tasks) >= 5:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)  # Rate limiting

        if not len(scraped_content):
            self.website_content.send([""])
            self.website_details.send([])
            return

        self.website_content.send([webpage.content for webpage in scraped_content])
        self.website_details.send(scraped_content)
