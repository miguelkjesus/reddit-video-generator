import asyncio, reddit, yaml, random, re
from tts import tts
from fs_utils import mkdir
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, vfx
from moviepy.video.fx.all import crop


def get_config():
    with open("./config.yaml", "r") as f:
        return yaml.safe_load(f)


def crop_video(clip, aspect_ratio: tuple[int, int]):
    w, h = clip.size
    target_width = int(h * aspect_ratio[0] / aspect_ratio[1])
    return crop(clip, width=target_width, height=h, x_center=w/2, y_center=h/2)


async def main():
    config = get_config()
    
    outdir = mkdir("./out")
    for subreddit in config["subreddits"]:
        subdir = mkdir(f"{outdir}/{subreddit}")
        for i, post in enumerate(post["data"] for post in reddit.top(subreddit)["data"]["children"]):
            postdir = mkdir(f"{subdir}/{i}")
            voice = random.choice(config["voices"])

            mp3Paths = []
            pngPaths = []

            # get title stuff
            titleMp3Path = f"{postdir}/title.mp3"
            tts(post["title"], voice, titleMp3Path)
            mp3Paths.append(titleMp3Path)

            titlePngPath = f"{postdir}/title.png"
            await reddit.get_title_image(post, titlePngPath)
            pngPaths.append(titlePngPath)

            # get description stuff
            if len(post["selftext"]) > 0:
                pgsdir = mkdir(f"{postdir}/paragraphs")
                paragraphs = [x for x in re.split("\n+", post["selftext"]) if len(x) > 0]
                for i, pg in enumerate(paragraphs):
                    paragraphMp3Filename = f"{pgsdir}/{i}.mp3"
                    tts(pg, voice, paragraphMp3Filename)
                    mp3Paths.append(paragraphMp3Filename)
                    
                    paragraphPngFilename = f"{pgsdir}/{i}.png"
                    await reddit.get_text_image(pg, paragraphPngFilename)
                    pngPaths.append(paragraphPngFilename)
            
            clip = crop_video(VideoFileClip(random.choice(config["videos"])), (9, 16))

            padding = 20

            start = 10
            t = start
            clips = []
            for mp3Path, pngPath in zip(mp3Paths, pngPaths):
                audio = AudioFileClip(mp3Path)
                portion = clip.subclip(t, t + audio.duration).set_audio(audio)
                image = ImageClip(pngPath).set_duration(audio.duration)
                target_height = image.size[1] * (portion.size[0] - 2 * padding) / image.size[0]
                image = image.resize(width=portion.size[0], height=target_height)
                image = image.set_position(((portion.size[0] - image.size[0]) // 2, (portion.size[1] - image.size[1]) // 2))
                clips.append(CompositeVideoClip([portion, image]).set_start(t - start))
                t += audio.duration

            # add subscribe clip
            scale = 0.3
            subscribe_clip = VideoFileClip("./videos/subscribe.mp4")
            subscribe_clip = (subscribe_clip
                              .resize(width=subscribe_clip.size[0] * scale, height=subscribe_clip.size[1] * scale)
                              .fx(vfx.mask_color, color=[0, 255, 8], thr=180, s=5)
                              .set_start(5))
            subscribe_clip = subscribe_clip.set_position(((clip.size[0] - subscribe_clip.size[0]) // 2, padding))

            clip = CompositeVideoClip([*clips, subscribe_clip]).subclip(0, min(t, 59))
            clip.write_videofile(f"{postdir}/video.mp4", fps=30)


if __name__ == "__main__":
    asyncio.run(main())
