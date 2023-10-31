import asyncio
import os
from typing import Dict
from dataclasses import dataclass

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

async def record_video(
    camera: Camera,
    filename: str = "test.mp4",
    output_dir: str = os.environ["DATA_DIR"],
    duration: int = 1,
    fps: int = 30,
) -> None:
    print(f"Recording video with {camera.name}")
    output_path = os.path.join(output_dir, filename),
    log: str = ""
    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-r", str(fps),
        "-t", str(duration),
        "-video_size", f"{camera.width}x{camera.height}",
        "-i", camera.device,
        "-c:v", "h264",
        output_path
    ]
    log += "Recording video using " + " ".join(cmd)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        log += f"ERROR on record: {stderr.decode()}"
    else:
        log += "Sucessfully recorded video."
    return log


async def take_image(
    camera: Camera,
    filename: str = "test.png",
    output_dir: str = os.environ["DATA_DIR"],
) -> None:
    print(f"Taking image with {camera.name}")
    output_path: str = os.path.join(output_dir, filename)
    log: str = ""
    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-video_size", f"{camera.width}x{camera.height}",
        "-i", camera.device,
        "-vframes", "1",
        output_path
    ]
    log += "Taking image using " + " ".join(cmd)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        log += f"ERROR on image capture: {stderr.decode()}"
    else:
        log += "Sucessfully took image."
    return log


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
