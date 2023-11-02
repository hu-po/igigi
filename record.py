import asyncio
import os
from typing import Any, Dict

from hparams import HPARAMS, Camera
from utils import async_timeout


@async_timeout(timeout=HPARAMS["timeout_record_video"])
async def record_video(
    camera: Camera,
    filename: str = "test.mp4",
    output_dir: str = os.environ["DATA_DIR"],
    duration: int = HPARAMS["video_duration"],
    fps: int = HPARAMS["video_fps"],
) -> Dict[str, Any]:
    output_path: str = os.path.join(output_dir, filename)
    process = await asyncio.create_subprocess_exec(
        *[
            "ffmpeg",
            "-y",
            "-f",
            "v4l2",
            "-r",
            str(fps),
            "-t",
            str(duration),
            "-video_size",
            f"{camera.width}x{camera.height}",
            "-i",
            camera.device,
            "-c:v",
            "h264",
            output_path,
        ],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        return {
            "log": f"Error on video capture: {stderr.decode()}",
            "output_path": output_path,
        }
    else:
        return {
            "log": f"Video from {camera.name} saved to {filename}. Duration: {duration} seconds. Size {camera.width}x{camera.height} at {fps} fps.",
            "output_path": output_path,
        }


@async_timeout(timeout=HPARAMS["timeout_take_image"])
async def take_image(
    camera: Camera,
    filename: str = HPARAMS["image_filename"],
    output_dir: str = HPARAMS["robot_data_dir"],
) -> Dict[str, Any]:
    output_path: str = os.path.join(output_dir, filename)
    process = await asyncio.create_subprocess_exec(
        *[
            "ffmpeg",
            "-y",
            "-f",
            "v4l2",
            "-video_size",
            f"{camera.width}x{camera.height}",
            "-i",
            camera.device,
            "-vframes",
            "1",
            output_path,
        ],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        return {
            "log": f"Error on image capture: {stderr.decode()}",
        }
    else:
        return {
            "log": f"Image from {camera.name} saved to {filename}. Size {camera.width}x{camera.height}.",
            "output_path": output_path,
        }


async def test_cameras():
    for name, camera in HPARAMS['cameras'].items():
        print(f"Testing camera {name}")
        result = await take_image(camera, f"test.{name}.png")
        print(result)
        result = await record_video(camera, f"test.{name}.mp4")
        print(result)


if __name__ == "__main__":
    asyncio.run(test_cameras())
