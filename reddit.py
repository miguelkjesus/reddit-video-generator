import requests, os, re
from typing import Literal
from datetime import datetime, timezone
from math import floor
from pyppeteer import launch

from utils import human_format
from fs_utils import read, write

def top(subreddit: str, duration: None | Literal["today", "week", "month", "year", "all"] = None) -> dict:
    durationParam = f"/?t={duration}" if duration is not None else ""
    return requests.get(
        f"https://www.reddit.com/r/{subreddit}/top{durationParam}/.json",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }
    ).json()


def format_template_html(templatedir: str, **formatKwargs: str) -> None:
    htmlTemplate = read(f"{templatedir}/template.html")
    html = htmlTemplate.format(**formatKwargs)
    write(f"{templatedir}/index.html", html)


async def web_to_image(url: str, path: str = None) -> bytes | str:
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {"waitUntil": ["domcontentloaded", "networkidle0"]})
    width, height = await page.evaluate("() => [document.documentElement.offsetWidth, document.documentElement.offsetHeight]")

    options = {
        "clip": {
            "x": 0,
            "y": 0,
            "width": width,
            "height": height
        },
        "omitBackground": True
    }
    if path is not None:
        options = options | {"path": path}
        
    img = await page.screenshot(options)
    await browser.close()
    return img


async def get_title_image(post: dict, path: str = None) -> bytes | str:
    templatedir = "./templates/title"

    hours_ago = (datetime.now(timezone.utc).timestamp() - post["created_utc"]) / 3600
    format_template_html(templatedir, 
        author=post["author"], 
        hours=floor(hours_ago), 
        title=post["title"], 
        upvotes=human_format(post["ups"]), 
        comments=human_format(post["num_comments"])
    )

    return await web_to_image(f"file:///{os.path.abspath(f'{templatedir}/index.html')}", path)


async def get_text_image(text: str, path: str = None) -> bytes | str:
    templatedir = "./templates/text"
    format_template_html(templatedir, text=text)
    return await web_to_image(f"file:///{os.path.abspath(f'{templatedir}/index.html')}", path)
