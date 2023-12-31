import asyncio
import os
import cv2
import numpy as np
from typing import Any, Dict

from hparams import HPARAMS, Camera
from utils import clear_data

class OpenCVCam:
    def __init__(self, camera: Camera = HPARAMS["camera"]):
        self.camera: Camera = camera
        self.cap = cv2.VideoCapture(camera.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera.height)
        if not self.cap.isOpened():
            raise ValueError(f"Error opening camera {camera.device}")


    async def take_image(
        self,
        filename: str = HPARAMS["image_filename"],
        output_dir: str = HPARAMS["robot_data_dir"],
        flip_vertical: bool = True,
        stereo_focus: np.ndarray = HPARAMS["stereo_focus"],
    ) -> Dict[str, Any]:
        output_path: str = os.path.join(output_dir, filename)
        if not self.cap.isOpened():
            return {"log": f"{HPARAMS['image_token']}{HPARAMS['fail_token']} camera not open"}
        
        ret, frame = self.cap.read()
        if ret:
            if flip_vertical:  # Flip the image if needed
                frame = cv2.flip(frame, 0)
            h, w, _ = frame.shape
            if stereo_focus is not None:
                # Calculate the bounding boxes for both eyes
                w, h = stereo_focus[0]
                x1, y1 = stereo_focus[1]
                x2, y2 = stereo_focus[2]
                half_h = h//2
                half_w = w//2
                left_clipped = frame[y1-half_h:y1+half_h, x1-half_w:x1+half_w]
                right_clipped = frame[y2-half_h:y2+half_h, x2-half_w:x2+half_w] 
                print(f"left: {x1}, {y1}, {w}, {h}")
                print(f"right: {x2}, {y2}, {w}, {h}")
                print(f"left clipped: {left_clipped.shape}")
                print(f"right clipped: {right_clipped.shape}")
                cv2.imwrite(output_path, cv2.hconcat([left_clipped, right_clipped]))
            else:
                cv2.imwrite(output_path, frame)
            return {
                "log": f"{HPARAMS['image_token']} image captured",
                "image_path" : output_path,
            }
        else:
            return {"log": f"{HPARAMS['image_token']}{HPARAMS['fail_token']} frame empty"}

    async def record_video(
        self,
        camera_name,
        filename: str = HPARAMS["video_filename"],
        output_dir: str = HPARAMS["robot_data_dir"],
        duration: int = HPARAMS["video_duration"],
        fps: int = HPARAMS["video_fps"],
        flip_vertical: bool = False,
    ) -> Dict[str, Any]:
        pass

    def __del__(self):
        self.cap.release()
        pass

async def test():
    print("testing camera")
    cam = OpenCVCam()
    await clear_data("robot")
    result = await cam.take_image()
    print(result)
    # result = await cam.record_video("test.mp4")
    # print(result)

if __name__ == "__main__":
    asyncio.run(test())
