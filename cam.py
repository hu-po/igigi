import asyncio
import os
import cv2
import numpy as np
from typing import Any, Dict

from hparams import HPARAMS, Camera

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
        return {"log": f"{HPARAMS['video_token']} error opening camera {camera.device}"}
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
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
        "log": f"{HPARAMS['video_token']} recorded video of {duration} seconds of size {camera.width}x{camera.height} at {fps} fps",
        "video_output_path": output_path,
    }

async def take_image(
    camera: Camera,
    filename: str = HPARAMS["image_filename"],
    output_dir: str = HPARAMS["robot_data_dir"],
    flip_vertical: bool = True,  
    stereo_focus: np.ndarray = HPARAMS["stereo_focus"],
) -> Dict[str, Any]:
    output_path: str = os.path.join(output_dir, filename)
    
    cap = cv2.VideoCapture(camera.device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera.height)
    if not cap.isOpened():
        return {"log": f"{HPARAMS['image_token']} error opening camera {camera.device}"}
    
    ret, frame = cap.read()
    if ret:
        if flip_vertical:  # Flip the image if needed
            frame = cv2.flip(frame, 0)
        if stereo_focus is not None:
            # Split the image vertically down the middle
            w, h = frame.shape[1] // 2, frame.shape[0]
            left_img, right_img = frame[:, :w], frame[:, w:2*w]
            
            # Calculate the bounding boxes for both eyes
            w, h = stereo_focus[0]
            x1, y1 = stereo_focus[1]
            x2, y2 = stereo_focus[2]
            x1, y1 = int(x1 - w//2), int(y1 - h//2)
            x2, y2 = int(x2 - w//2), int(y2 - h//2)
            left_clipped = left_img[y1:y1+h, x1:x1+w]
            right_clipped = right_img[y2:y2+h, x2:x2+w]

            cv2.imwrite(output_path+".png", cv2.hconcat([left_clipped, right_clipped]))
        else:
            cv2.imwrite(output_path, frame)
    else:
        return {"log": f"{HPARAMS['image_token']} error capturing image from {camera.device}"}
    
    cap.release()

async def test_cameras():
    for name, camera in HPARAMS['cameras'].items():
        print(f"Testing camera {name}")
        result = await take_image(camera, f"test.{name}.png")
        print(result)
        result = await record_video(camera, f"test.{name}.mp4")
        print(result)
        # from utils import send_file
        # result = await send_file("test_img", "robot", "brain", _filename=f"test.{name}.png")
        # result = await send_file("test_vid", "robot", "brain", _filename=f"test.{name}.mp4")

if __name__ == "__main__":
    asyncio.run(test_cameras())
