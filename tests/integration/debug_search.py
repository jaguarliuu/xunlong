"""调试搜索功能"""

import asyncio
from playwright.async_api import async_playwright


async def debug_duckduckgo():
    """调试DuckDuckGo搜索"""
    print("🔍 调试DuckDuckGo搜索...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器
        page = await browser.new_page()
        
        try:
            # 访问DuckDuckGo
            print("📱 访问DuckDuckGo...")
            await page.goto("https://duckduckgo.com/", wait_until="networkidle")
            
            # 输入搜索词
            print("🔍 输入搜索词...")
            search_input = page.locator('input[name="q"]')
            await search_input.fill("Python")
            await search_input.press("Enter")
            
            # 等待页面加载
            print("⏳ 等待页面加载...")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # 获取页面HTML用于分析
            html = await page.content()
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("💾 页面HTML已保存到 debug_page.html")
            
            # 尝试找到搜索结果
            print("🔍 查找搜索结果元素...")
            
            # 尝试各种可能的选择器
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
                    print(f"✅ 找到 {count} 个元素: {selector}")
                    found_elements.append((selector, count))
                    
                    # 获取前几个元素的信息
                    elements = await page.locator(selector).all()
                    for i, element in enumerate(elements[:3]):
                        try:
                            text = await element.inner_text()
                            print(f"   元素 {i+1}: {text[:100]}...")
                        except:
                            print(f"   元素 {i+1}: 无法获取文本")
                else:
                    print(f"❌ 未找到元素: {selector}")
            
            if found_elements:
                print(f"\n🎉 找到 {len(found_elements)} 种可用选择器")
                # 使用第一个找到的选择器尝试提取链接
                best_selector = found_elements[0][0]
                print(f"🔗 使用选择器 {best_selector} 提取链接...")
                
                elements = await page.locator(best_selector).all()
                for i, element in enumerate(elements[:3]):
                    try:
                        # 尝试找到链接
                        link_element = element.locator('a').first
                        if await link_element.count() > 0:
                            href = await link_element.get_attribute('href')
                            text = await link_element.inner_text()
                            print(f"   链接 {i+1}: {text[:50]} -> {href}")
                    except Exception as e:
                        print(f"   链接 {i+1}: 提取失败 - {e}")
            else:
                print("❌ 未找到任何搜索结果元素")
            
            # 截图保存
            await page.screenshot(path="debug_screenshot.png")
            print("📸 调试截图已保存到 debug_screenshot.png")
            
        except Exception as e:
            print(f"❌ 调试过程中出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    print("🐛 DuckDuckGo 搜索调试工具")
    print("="*40)
    
    try:
        asyncio.run(debug_duckduckgo())
        print("\n✅ 调试完成！请查看生成的文件:")
        print("- debug_page.html: 页面HTML源码")
        print("- debug_screenshot.png: 页面截图")
    except KeyboardInterrupt:
        print("\n⏹️ 调试被用户中断")
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()