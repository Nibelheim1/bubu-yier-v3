"""V3 hands-on: screenshots of every screen + verify the three claimed fixes."""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(r'E:\Desktop\BubuYier_V3')
SHOT = ROOT / 'qa' / 'v3review'; SHOT.mkdir(parents=True, exist_ok=True)
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = 'http://127.0.0.1:4190/index.html?debug=1'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME, headless=True,
                                         args=['--no-sandbox', '--enable-unsafe-swiftshader', '--mute-audio'])
        page = await browser.new_page(viewport={'width': 960, 'height': 540})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        reqs = []
        page.on('response', lambda r: reqs.append((r.url.split('/')[-1], r.status)))
        await page.goto(BASE)
        await page.wait_for_selector('#begin', timeout=25000)
        await page.wait_for_timeout(1200)
        await page.screenshot(path=str(SHOT / 'v3_title.png'))
        print('title texts:', ' | '.join((await page.inner_text('#ui')).split('\n'))[:400])
        print('images loaded so far:', [n for n, s in reqs if n.endswith('.png')])
        await page.click('#begin'); await page.wait_for_selector('.character-card')
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SHOT / 'v3_characters.png'))
        await page.click('#choose-role'); await page.wait_for_timeout(1200)
        await page.screenshot(path=str(SHOT / 'v3_level1_start.png'))
        print('errors:', errs)
        print('all image requests:', [n for n, s in reqs if n.endswith('.png')])
        await browser.close()

asyncio.run(main())
