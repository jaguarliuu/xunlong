"""TODO: Add docstring."""

import asyncio
from playwright.async_api import async_playwright


async def debug_duckduckgo():
    """DuckDuckGo"""
    print(" DuckDuckGo...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 
        page = await browser.new_page()
        
        try:
            # DuckDuckGo
            print(" DuckDuckGo...")
            await page.goto("https://duckduckgo.com/", wait_until="networkidle")
            
            # 
            print(" ...")
            search_input = page.locator('input[name="q"]')
            await search_input.fill("Python")
            await search_input.press("Enter")
            
            # 
            print(" ...")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # HTML
            html = await page.content()
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(" HTML debug_page.html")
            
            # 
            print(" ...")
            
            # 
            selectors = [
                '[data-testid="result"]',
                '.result',
                'article',
                '[data-layout="organic"]',
                '.web-result',
                '.result__body',
                'div[data-testid]',
                'div.result',
                'div[class*="result"]',
                'h2 a',
                'a[data-testid="result-title-a"]',
                '.result__a'
            ]
            
            found_elements = []
            for selector in selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    print(f"  {count} : {selector}")
                    found_elements.append((selector, count))
                    
                    # 
                    elements = await page.locator(selector).all()
                    for i, element in enumerate(elements[:3]):
                        try:
                            text = await element.inner_text()
                            print(f"    {i+1}: {text[:100]}...")
                        except:
                            print(f"    {i+1}: ")
                else:
                    print(f" : {selector}")
            
            if found_elements:
                print(f"\n  {len(found_elements)} ")
                # 
                best_selector = found_elements[0][0]
                print(f"  {best_selector} ...")
                
                elements = await page.locator(best_selector).all()
                for i, element in enumerate(elements[:3]):
                    try:
                        # 
                        link_element = element.locator('a').first
                        if await link_element.count() > 0:
                            href = await link_element.get_attribute('href')
                            text = await link_element.inner_text()
                            print(f"    {i+1}: {text[:50]} -> {href}")
                    except Exception as e:
                        print(f"    {i+1}:  - {e}")
            else:
                print(" ")
            
            # 
            await page.screenshot(path="debug_screenshot.png")
            print("  debug_screenshot.png")
            
        except Exception as e:
            print(f" : {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    print(" DuckDuckGo ")
    print("="*40)
    
    try:
        asyncio.run(debug_duckduckgo())
        print("\n :")
        print("- debug_page.html: HTML")
        print("- debug_screenshot.png: ")
    except KeyboardInterrupt:
        print("\n ")
    except Exception as e:
        print(f"\n : {e}")
        import traceback
        traceback.print_exc()