import asyncio
import os
import cv2
from typing import Any, Dict

from hparams import HPARAMS, Camera
from utils import async_task

@async_task(timeout=HPARAMS["timeout_record_video"])
async def record_video(
    camera: Camera,
    filename: str = HPARAMS["video_filename"],
    output_dir: str = HPARAMS["robot_data_dir"],
    duration: int = HPARAMS["video_duration"],
    fps: int = HPARAMS["video_fps"],
    flip_vertical: bool = False,   # <-- New kwarg
) -> Dict[str, Any]:
    output_path: str = os.path.join(output_dir, filename)
    
    cap = cv2.VideoCapture(camera.device)
    if not cap.isOpened():
        return {"log": f"Error opening camera {camera.device}", "video_output_path": output_path}
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (camera.width, camera.height))
    
    for _ in range(int(fps * duration)):
        ret, frame = cap.read()
        if ret:
            if flip_vertical:  # Flip the image if needed
                frame = cv2.flip(frame, 0)
            out.write(frame)
        else:
            break
    
    cap.release()
    out.release()

    return {
        "log": f"Video from saved to {filename}. Duration: {duration} seconds. Size {camera.width}x{camera.height} at {fps} fps.",
        "video_output_path": output_path,
    }

@async_task(timeout=HPARAMS["timeout_take_image"])
async def take_image(
    camera: Camera,
    filename: str = HPARAMS["image_filename"],
    output_dir: str = HPARAMS["robot_data_dir"],
    flip_vertical: bool = True,   # <-- New kwarg
) -> Dict[str, Any]:
    output_path: str = os.path.join(output_dir, filename)
    
    cap = cv2.VideoCapture(camera.device)
    if not cap.isOpened():
        return {"log": f"Error opening camera {camera.device}"}
    
    ret, frame = cap.read()
    if ret:
        if flip_vertical:  # Flip the image if needed
            frame = cv2.flip(frame, 0)
        cv2.imwrite(output_path, frame)
    else:
        return {"log": f"Error capturing image from {camera.device}"}
    
    cap.release()

    return {
        "log": f"Image from saved to {filename}. Size {camera.width}x{camera.height}.",
        "image_output_path": output_path,
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
