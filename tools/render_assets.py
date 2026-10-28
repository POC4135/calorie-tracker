#!/usr/bin/env python3
"""Render the plugin icon and the GitHub social preview from docs/assets/src.

    python tools/render_assets.py

Needs Playwright with Chromium (pip install playwright && playwright install chromium).
Outputs: .claude-plugin/icon.png (1024x1024) and docs/assets/social-preview.png (1280x640).
"""

import asyncio
import os
import shutil

from playwright.async_api import async_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "docs", "assets", "src")
ICON = os.path.join(ROOT, ".claude-plugin", "icon.png")
PREVIEW = os.path.join(ROOT, "docs", "assets", "social-preview.png")


async def render():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1024, "height": 1024})
        with open(os.path.join(SRC, "icon.svg"), encoding="utf-8") as handle:
            svg = handle.read()
        await page.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
        await page.screenshot(path=ICON, omit_background=True, clip={"x": 0, "y": 0, "width": 1024, "height": 1024})
        # The preview page shows the icon from its own folder.
        temp_icon = os.path.join(SRC, "icon.png")
        shutil.copyfile(ICON, temp_icon)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 640})
            await page.goto("file://" + os.path.join(SRC, "social-preview.html"))
            await page.wait_for_timeout(300)
            await page.screenshot(path=PREVIEW)
        finally:
            os.remove(temp_icon)
        await browser.close()
    print(f"wrote {ICON}\nwrote {PREVIEW}")


if __name__ == "__main__":
    asyncio.run(render())
