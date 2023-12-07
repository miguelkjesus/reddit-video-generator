import requests, os
from typing import Literal
from utils import human_format
from datetime import datetime, timezone
from math import floor
from pyppeteer import launch

def top(subreddit: str, duration: None | Literal["today", "week", "month", "year", "all"] = None) -> dict:
    durationParam = f"/?t={duration}" if duration is not None else ""
    return requests.get(
        f"https://www.reddit.com/r/{subreddit}/top{durationParam}/.json",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }
    ).json()


async def web_to_image(url: str, path: str = None) -> bytes:
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
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


async def post_to_title_image(post: dict, path: str = None) -> bytes | str:
    htmlTemplate = ""
    with open("./templates/title/template.html") as f:
        htmlTemplate = f.read()

    hours_ago = (datetime.now(timezone.utc).timestamp() - post["created_utc"]) / 60 / 60
    html = htmlTemplate.format(
        author=post["author"], 
        hours=floor(hours_ago), 
        title=post["title"], 
        upvotes=human_format(post["ups"]), 
        comments=human_format(post["num_comments"])
    )

    with open("./templates/title/index.html", "w") as f:
        f.write(html)

    await web_to_image(f"file:///{os.path.abspath('./templates/title/index.html')}", path)
