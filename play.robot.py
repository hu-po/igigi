import asyncio
import os
import sys
import logging

from .gpt import gpt_text
from .utils import scrape_callback, send_file
from .record import take_image, record_video
from .servos import move_with_prompt

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

async def main_loop():
    
    """
    scrape for user commands
    scrape for image + image log
    scrape for servo + servo log

    ask llm for servo commands, write servo commands, send servo commands
    ask llm for image commands, write image commands, send image commands
    """

    log.setLevel(logging.DEBUG)
    log.debug(f"Testing cameras: {CAMERAS}")
    log.debug("Testing take_image")
    image_tasks = [take_image(camera) for camera in CAMERAS]
    results = await asyncio.gather(*image_tasks, return_exceptions=True)
    
    log.debug("Testing record_video")
    video_tasks = [record_video(camera) for camera in CAMERAS]
    results = await asyncio.gather(*video_tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main_loop())
