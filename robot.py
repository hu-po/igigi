import asyncio
import os
import sys

from .hparams import HPARAMS
from .utils import scrape_callback, send_file, llm_func
from .record import take_image, record_video
from .servos import move_with_prompt

async def main_loop(hparams: dict):

    # receive servo commands from brain
    scrape_callback(
        hparams.get("brain_data_dir"),
        hparams.get("commands_filename"),
        llm_func,
        hparams.get("interval"),
        hparams.get("timeout"),
    )

    # initialize robot

    # take image

    # send image to brain
    send_file(
        filename: str,
        local_dir_path: str,
        remote_dir_path: str,
        remote_username: str,
        remote_ip: str,
    )

    # move servos based on commands

    image_tasks = [take_image(camera) for camera in CAMERAS]
    results = await asyncio.gather(*image_tasks, return_exceptions=True)

    video_tasks = [record_video(camera) for camera in CAMERAS]
    results = await asyncio.gather(*video_tasks, return_exceptions=True)

async def test(hparams: dict):
    pass


if __name__ == "__main__":
    asyncio.run(test())
    asyncio.run(main_loop())
