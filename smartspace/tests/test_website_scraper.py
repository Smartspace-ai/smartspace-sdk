import pytest

from smartspace.blocks.website_scraper import WebsiteScraper


@pytest.mark.asyncio
async def test_make_request_get():
    w = WebsiteScraper()
    w.page_limit = 1
    await w.scrape_website("https://google.com")
    messages = w.get_messages()
    assert len(messages[0].outputs[0].value) == 1  # 1 message should be sent
    assert (
        "Google" in messages[0].outputs[0].value[0]
    )  # Google should be in the scraped content


@pytest.mark.asyncio
async def test_make_request_error():
    w = WebsiteScraper()
    w.page_limit = 1
    await w.scrape_website("https://dummyjson.com/http/404/Hello_Peter")
    messages = w.get_messages()
    assert len(messages[0].outputs[0].value) == 1
    assert messages[0].outputs[0].value[0] == ""


@pytest.mark.asyncio
async def test_make_request_multiple_pages():
    w = WebsiteScraper()
    page_limit = 3
    w.page_limit = page_limit
    await w.scrape_website("https://google.com")
    messages = w.get_messages()
    assert len(messages[0].outputs[0].value) == page_limit
    assert any("Google" in output.value[0] for output in messages[0].outputs)


@pytest.mark.asyncio
async def test_make_request_no_url():
    w = WebsiteScraper()
    w.page_limit = 1
    await w.scrape_website("")
    messages = w.get_messages()
    assert len(messages[0].outputs[0].value) == 1
    assert messages[0].outputs[0].value[0] == ""


@pytest.mark.asyncio
async def test_make_request_invalid_url():
    w = WebsiteScraper()
    w.page_limit = 1
    await w.scrape_website("invalid_url")
    messages = w.get_messages()
    assert len(messages[0].outputs[0].value) == 1
    assert messages[0].outputs[0].value[0] == ""
