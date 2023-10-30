import asyncio
import os
import sys

from .hparams import HPARAMS
from .utils import scrape_callback, send_file, llm_func
from .record import take_image, record_video
from .servos import move_with_prompt

async def move_with_prompt(
    robot: Robot,
    llm_func: callable,
    raw_move_str: int,
    system_msg: str = SYSTEM_PROMPT,
    move_msg: str = MOVE_MSG,
) -> str:
    msg: str = ""
    desired_pose_name = llm_func(
            max_tokens=8,
            messages=[
                {"role": "system", "content": f"{system_msg}\n{move_msg}"},
                {"role": "user", "content": raw_move_str},
            ]
    )
    msg += f"{MOVE_TOKEN} commanded pose is {desired_pose_name}\n"
    desired_pose = POSES.get(desired_pose_name, None)
    if desired_pose is not None:
        return robot.move(desired_pose.angles)
    else:
        msg += f"ERROR: {desired_pose_name} is not a valid pose.\n"
        return msg


def test_servos_llm() -> None:
    log.setLevel(logging.DEBUG)
    log.debug("Testing move with prompt")
    robot = Robot()
    from .gpt import gpt_text
    for raw_move_str in [
        "go to the home position",
        "check on your left",
        "bogie on your right",
        "what is on the floor",
    ]:
        msg = move_with_prompt(robot, gpt_text, raw_move_str)
        print(msg)
        time.sleep(1)
    del robot

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
