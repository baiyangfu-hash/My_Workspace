# ruff: noqa: T201
import asyncio
import os

from playwright.async_api import async_playwright

PROTOTYPE_PATH = r"c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\02_设计\GUI原型.html"
OUTPUT_DIR = r"c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\02_设计\figma_screenshots"

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}


async def take_screenshot(page, filename, viewport_name):
    filepath = os.path.join(OUTPUT_DIR, filename)
    await page.screenshot(path=filepath, full_page=True)
    print(f"✅ {filename} ({viewport_name})")


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            headless=True
        )
        
        for viewport_name, viewport in VIEWPORTS.items():
            page = await browser.new_page(viewport=viewport)
            
            url = f"file:///{PROTOTYPE_PATH}"
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            await take_screenshot(page, f"01_home_{viewport_name}.png", viewport_name)
            
            try:
                await page.click("#nav-change")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"02_change_center_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-change ({viewport_name}) - {str(e)}")
            
            try:
                await page.click("#nav-spec")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"03_spec_center_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-spec ({viewport_name}) - {str(e)}")
            
            try:
                await page.click("#nav-template")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"04_template_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-template ({viewport_name}) - {str(e)}")
            
            try:
                await page.click("#nav-report")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"05_report_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-report ({viewport_name}) - {str(e)}")
            
            try:
                await page.click("#nav-settings")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"06_settings_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-settings ({viewport_name}) - {str(e)}")
            
            try:
                await page.click("#nav-all")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"07_project_list_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 导航失败: nav-all ({viewport_name}) - {str(e)}")
            
            try:
                await page.click(".project-card")
                await page.wait_for_timeout(500)
                await take_screenshot(page, f"08_workspace_overview_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ 打开工作区失败 ({viewport_name}) - {str(e)}")
            
            try:
                tabs = ["变更", "检查", "文档", "变量表"]
                for tab_name in tabs:
                    await page.click(f'button.tab-btn:has-text("{tab_name}")')
                    await page.wait_for_timeout(500)
                    tab_index = tabs.index(tab_name) + 9
                    await take_screenshot(page, f"{tab_index:02d}_workspace_{tab_name}_{viewport_name}.png", viewport_name)
            except Exception as e:
                print(f"⚠️ Tab切换失败 ({viewport_name}) - {str(e)}")
            
            await page.close()
        
        await browser.close()
    
    print(f"\n🎉 截图完成！保存在 {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())