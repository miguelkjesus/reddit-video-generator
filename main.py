import asyncio, reddit, yaml, random, re
from tts import tts
from fs_utils import mkdir

def get_config():
    with open("./config.yaml", "r") as f:
        return yaml.safe_load(f)

async def main():
    config = get_config()
    
    outdir = mkdir("./out")
    for subreddit in config["subreddits"]:
        subdir = mkdir(f"{outdir}/{subreddit}")

        for i, post in enumerate(post["data"] for post in reddit.top(subreddit)["data"]["children"]):
            postdir = mkdir(f"{subdir}/{i}")
            voice = random.choice(config["voices"])

            # title
            tts(post["title"], voice, f"{postdir}/title.mp3")
            await reddit.get_title_image(post, f"{postdir}/title.png")

            # description
            if len(post["selftext"]) > 0:
                pgsdir = mkdir(f"{postdir}/paragraphs")
                paragraphs = [x for x in re.split("\n+", post["selftext"]) if len(x) > 0]
                for i, pg in enumerate(paragraphs):
                    tts(pg, voice, f"{pgsdir}/{i}.mp3")
                    await reddit.get_text_image(pg, f"{pgsdir}/{i}.png")
                


if __name__ == "__main__":
    asyncio.run(main())
