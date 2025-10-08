# Chapter 1 · Driving DuckDuckGo with Playwright

This chapter opens the “XunLong Internals” tutorial series. We unpack how the project performs web search today and why it orchestrates a full browser instead of using crawler APIs.

---

## 1. Why a Headless Browser?

XunLong’s search stack is built around Playwright (see `src/tools/web_searcher.py`). The coordinator spins up a Chromium instance (`src/browser.py`) and automates DuckDuckGo, then reuses the same runtime to visit each result.

We take the browser-driven path for three reasons:

1. **Dynamic Content Everywhere**  
   Many sources load text after initial request or hide copy behind scripts. A headless browser waits for the network to become idle and scrolls the page (`BrowserManager.wait_for_page_load`), guaranteeing the DOM contains what the writer agents need.

2. **Consistent Extraction & Screenshots**  
   The HTML we gather is later converted to Markdown/HTML/PDF and sometimes needs screenshots. Driving the same Chromium instance for search and content extraction gives us predictable rendering and pixel-perfect captures (`browser.py:take_screenshot`).

3. **Rate Limits & Coverage**  
   API aggregators such as Firecrawl are fantastic, but they:
   - only expose a subset of the public web,
   - add an extra vendor dependency with per-request quotas, and
   - often omit embedded media or paywalled previews that Playwright can see with human-like interaction.

By handling DuckDuckGo in-house we keep control of throttling, caching, and fallback logic while staying API-key agnostic.

---

## 2. How Search Works in XunLong

The search pipeline is a chain of specialised modules:

| Step | File | Responsibility |
| ---- | ---- | -------------- |
| **1. Task planning** | `src/agents/task_decomposer.py` | Breaks the user query into focused sub-tasks (possibly constrained by uploaded documents). |
| **2. Browser orchestration** | `src/browser.py` | Starts Playwright, configures headless/headful mode, handles anti-bot tweaks. |
| **3. DuckDuckGo automation** | `src/tools/web_searcher.py` | Submits the query, applies date filters, scrapes result cards, and optionally captures screenshots. |
| **4. Full-page extraction** | `src/pipeline.py` + `src/tools/web_searcher.py::_fetch_full_content_with_browser` | Visits each URL, waits for JS, collects main text, images, metadata. |
| **5. Ranking & deduplication** | `src/agents/deep_searcher.py` | Merges results, prioritises user-uploaded documents, removes duplicates, ranks by relevance/time. |
| **6. Storage & reuse** | `src/storage/search_storage.py` | Persists intermediate JSON, human-readable summaries, and screenshots for iteration/export. |

Because the same Playwright session feeds all later stages, we guarantee consistent user-agent headers, locale, and cookie state across DuckDuckGo and the target sites.

---

## 3. Minimal Demo (`chapter1_playwright_duckduckgo.py`)

The tutorial branch includes a self-contained example at:

```
examples/tutorial/chapter1_playwright_duckduckgo.py
```

This script shows the bare minimum needed to drive DuckDuckGo, grab result titles & URLs, and close the browser politely.

### Prerequisites

```bash
pip install playwright
playwright install chromium
```

### Run the demo

```bash
python examples/tutorial/chapter1_playwright_duckduckgo.py "AI industry trends"
```

You should see the top results printed to the console.

---

## 4. What’s Next?

Chapter 2 will dive deeper into the extraction step—waiting for lazy-loaded content, handling paywall stubs, and piping everything into XunLong’s storage layer. Stay tuned!

