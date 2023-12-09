import asyncio, reddit, yaml, random, json
from fs_utils import mkdir, read, write
from construct_video import construct_video
from youtube_upload.client import YoutubeUploader

def get_config():
    return (yaml.safe_load(read("./config.yaml"))
            | json.loads(read("./client_secrets.json")))


async def main():
    config = get_config()

    # init youtube uploader
    if config["automatic-upload"]["enabled"]:
        uploader = YoutubeUploader()
        uploader.authenticate()
    
    # make videos
    outdir = mkdir("./out")
    for subreddit in config["subreddits"]:
        subdir = mkdir(f"{outdir}/{subreddit}")
        for postIdx, post in enumerate(post["data"] for post in reddit.top(subreddit)["data"]["children"]):
            if postIdx >= config["max-posts"]: break
            
            postdir = mkdir(f"{subdir}/{postIdx}")

            # generate upload options
            uploadOptions = {
                "title": f"r/{subreddit} Top Reddit Stories Today #{postIdx+1} #{subreddit} #reddit #redditstories #shorts",
                "description": "",
                "tags": [subreddit, "reddit", "redditstories", "shorts"],
                "categoryId": "42",  # Shorts catgeory id
                "privacyStatus": config["automatic-upload"]["visibility"],
                "kids": False,
                "thumbnailLink": ""
            }
            write(f"{postdir}/upload_options.yaml", yaml.dump(uploadOptions, sort_keys=False))

            # generate video
            videoPath = await construct_video(
                post, 
                postdir,
                random.choice(config["voices"]),
                random.choice(config["videos"]),
                config["max-video-length"]
            )

            # upload video if wanted
            if config["automatic-upload"]["enabled"]: 
                uploader.upload(videoPath, uploadOptions)
                print(f"Uploaded {videoPath}")


if __name__ == "__main__":
    asyncio.run(main())
