import asyncio
import os
from typing import Dict
from dataclasses import dataclass

DEFAULT_VIDEO_DURATION = 1 # seconds
DEFAULT_VIDEO_FPS = 30

@dataclass
class Camera:
    device: str
    name: str
    width: int
    height: int
    desc: str


CAMERAS: Dict[str, Camera] = {
    "stereo" : Camera(
        device="/dev/video0",
        name="stereo",
        width=1280,
        height=480,
        desc="stereo camera on the face facing forward",
    ),
    "mono" : Camera(
        device="/dev/video2",
        name="mono",
        width=640,
        height=480,
        desc="monocular camera on the chest facing forward",
    ),
}

async def record_video(camera: Camera, **hparams) -> None:
    duration: int = hparams.get("duration", DEFAULT_VIDEO_DURATION)
    fps: int = hparams.get("fps", DEFAULT_VIDEO_FPS)
    output_dir: str = hparams.get("robot_data_dir", os.environ["DATA_DIR"])
    video_filename: str = hparams.get("robot_video_filename", f"test.{camera.name}.mp4")
    videolog_filename: str = hparams.get("robot_videolog_filename", f"test.{camera.name}.txt")
    video_output_path = os.path.join(output_dir, video_filename)
    videolog_output_path = os.path.join(output_dir, videolog_filename)
    videolog: str = ""
    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-r", str(fps),
        "-t", str(duration),
        "-video_size", f"{camera.width}x{camera.height}",
        "-i", camera.device,
        "-c:v", "h264",
        video_output_path
    ]
    videolog += " ".join(cmd) + "\n"
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        videolog += f"ERROR on record: {stderr.decode()}"
    else:
        videolog += "recording successful\n"
    with open(videolog_output_path, "w") as f:
        f.write(videolog)


async def take_image(camera: Camera, **hparams) -> None:
    output_dir: str = hparams.get("robot_data_dir", os.environ["DATA_DIR"])
    image_filename: str = hparams.get("robot_image_filename", f"test.{camera.name}.png")
    imagelog_filename: str = hparams.get("robot_imagelog_filename", f"test.{camera.name}.txt")
    image_output_path = os.path.join(output_dir, image_filename)
    imagelog_output_path = os.path.join(output_dir, imagelog_filename)
    imagelog: str = ""
    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-video_size", f"{camera.width}x{camera.height}",
        "-i", camera.device,
        "-vframes", "1",
        image_output_path
    ]
    imagelog += " ".join(cmd) + "\n"
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        imagelog += f"ERROR on image capture: {stderr.decode()}"
    else:
        imagelog += "image capture successful\n"
    with open(imagelog_output_path, "w") as f:
        f.write(imagelog)


async def test_cameras():
    print(f"Testing cameras: {CAMERAS}")
    print("Testing take_image")
    image_tasks = [take_image(camera) for camera in CAMERAS.values()]
    _ = await asyncio.gather(*image_tasks, return_exceptions=True)
    print("Testing record_video")
    video_tasks = [record_video(camera) for camera in CAMERAS.values()]
    _ = await asyncio.gather(*video_tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(test_cameras())
