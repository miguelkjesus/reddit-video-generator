import reddit, re
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, vfx
from moviepy.video.fx.all import crop
from fs_utils import mkdir
from tts import tts

def set_aspect_ratio(clip, aspect_ratio: tuple[int, int]):
    w, h = clip.size
    target_width = int(h * aspect_ratio[0] / aspect_ratio[1])
    if target_width % 2 == 1:  # fixes an odd bug with odd dimension sizes corrupting videos
        target_width -= 1
    return crop(clip, width=target_width, height=h, x_center=w//2, y_center=h//2)


async def construct_video(post: dict, voice: str, bgVideoPath: str, maxVideoLength: float, outFolderPath: str) -> None:
    mp3Paths = []
    pngPaths = []

    # get title stuff
    titleMp3Path = f"{outFolderPath}/title.mp3"
    tts(post["title"], voice, titleMp3Path)
    mp3Paths.append(titleMp3Path)

    titlePngPath = f"{outFolderPath}/title.png"
    await reddit.get_title_image(post, titlePngPath)
    pngPaths.append(titlePngPath)

    # get description stuff
    if len(post["selftext"]) > 0:
        pgsdir = mkdir(f"{outFolderPath}/paragraphs")
        paragraphs = [x for x in re.split("\n+", post["selftext"]) if len(x) > 0]
        for pgIdx, pg in enumerate(paragraphs):
            paragraphMp3Filename = f"{pgsdir}/{pgIdx}.mp3"
            tts(pg, voice, paragraphMp3Filename)
            mp3Paths.append(paragraphMp3Filename)
            
            paragraphPngFilename = f"{pgsdir}/{pgIdx}.png"
            await reddit.get_text_image(pg, paragraphPngFilename)
            pngPaths.append(paragraphPngFilename)

    # build video
    videoPath=f"{outFolderPath}/video.mp4"
    build_video(
        bgVideoPath=bgVideoPath,
        mp3Paths=mp3Paths,
        pngPaths=pngPaths,
        outPath=videoPath,
        maxVideoLength=maxVideoLength
    )

    return videoPath


def build_video(bgVideoPath: str, outPath: str, mp3Paths: list[str], pngPaths: list[str], maxVideoLength: float) -> None:
    clip = VideoFileClip(bgVideoPath)
    clip = set_aspect_ratio(clip, (9, 16))

    start = 10
    t = start
    clips = []
    for mp3Path, pngPath in zip(mp3Paths, pngPaths):
        audio = AudioFileClip(mp3Path)
        portion = clip.subclip(t, t + audio.duration).set_audio(audio)
        image = ImageClip(pngPath).set_duration(audio.duration)
        target_height = image.size[1] * (portion.size[0] - 40) / image.size[0]
        image = image.resize(width=portion.size[0], height=target_height)
        image = image.set_position(((portion.size[0] - image.size[0]) // 2, (portion.size[1] - image.size[1]) // 2))
        clips.append(CompositeVideoClip([portion, image]).set_start(t - start))
        t += audio.duration

    # # add subscribe clip
    scale = 0.4
    subscribe_clip = VideoFileClip("./videos/subscribe.mp4")
    subscribe_clip = (subscribe_clip
                        .resize(width=subscribe_clip.size[0] * scale, height=subscribe_clip.size[1] * scale)
                        .fx(vfx.mask_color, color=[0, 255, 8], thr=180, s=5)
                        .set_start(5))
    subscribe_clip = subscribe_clip.set_position(((clip.size[0] - subscribe_clip.size[0]) // 2, 50))

    clip = CompositeVideoClip([*clips, subscribe_clip]).subclip(0, min(t, maxVideoLength))
    clip.write_videofile(outPath)
