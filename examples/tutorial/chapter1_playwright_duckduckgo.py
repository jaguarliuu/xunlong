"""
Chapter 1 demo: minimal Playwright automation for DuckDuckGo.

Run:
    playwright install chromium
    python chapter1_playwright_duckduckgo.py "AI industry trends"
"""

import asyncio
import sys
from typing import List

from playwright.async_api import async_playwright


async def search_duckduckgo(query: str, max_results: int = 5) -> List[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://duckduckgo.com/", wait_until="domcontentloaded")
        await page.fill("input[name='q']", query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)  # allow results to load

        results = []
        items = await page.locator("[data-testid='result']").all()
        for item in items[:max_results]:
            title = await item.locator("[data-testid='result-title-a']").inner_text()
            url = await item.locator("a[data-testid='result-title-a']").get_attribute("href")
            snippet_loc = item.locator("[data-testid='result-snippet']")
            snippet = await snippet_loc.inner_text() if await snippet_loc.count() else ""
            results.append({"title": title.strip(), "url": url, "snippet": snippet.strip()})

        await browser.close()
        return results


async def main():
    if len(sys.argv) < 2:
        print("Usage: python chapter1_playwright_duckduckgo.py \"your query\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Searching DuckDuckGo for: {query}\n")
    results = await search_duckduckgo(query)

    for idx, result in enumerate(results, start=1):
        print(f"{idx}. {result['title']}")
        print(f"   {result['url']}")
        if result['snippet']:
            print(f"   {result['snippet']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
