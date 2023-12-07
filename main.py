import asyncio, reddit, yaml, random
from tts import tts
from utils import mkdir

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

            tts(post["title"], voice, f"{postdir}/title.mp3")
            await reddit.post_to_title_image(post, f"{postdir}/title.png")


if __name__ == "__main__":
    asyncio.run(main())