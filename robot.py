import asyncio
import os

from hparams import HPARAMS
from utils import find_file, send_file, create_session_folder
from record import take_image, record_video, CAMERAS
from llm import move_servos
from servos import Servos
from app import ChromeUI


async def main_loop(servos: Servos, ui: ChromeUI):
    robot_log: str = ""
    # Batch 1: get commands, take mono image
    task_batch = [
        find_file(
            HPARAMS["commands_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
            HPARAMS["scrape_interval"],
            HPARAMS["scrape_timeout"],
        ),
        take_image(
            CAMERAS["mono"],
            HPARAMS["image_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
        ),
    ]
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    # Create new task batch
    task_batch = []
    # Moving servos requires a commands file
    robot_log += results[0]["log"]
    will_move_servos: bool = True
    if results[0]["full_path"] is None:
        robot_log += "No command file found."
        will_move_servos = False
    if results[0]["file_age"] < HPARAMS["commands_max_age"]:
        robot_log += "Command file is too old."
        will_move_servos = False
    if will_move_servos:
        robot_log += "Adding move_servos to tasks."
        task_batch.append(
            move_servos(
                servos,
                HPARAMS["robot_llm_system_prompt"],
                HPARAMS["commands_filename"],
                HPARAMS["robot_llm_model"],
                HPARAMS["robot_llm_temperature"],
                HPARAMS["robot_llm_max_tokens"],
            ),
        )
    # Sending image requires an error free image capture
    robot_log += results[1]["log"]
    if results[1].get("output_path") is not None:
        robot_log += "Adding send_file to tasks."
        task_batch.append(
            send_file(
                HPARAMS["image_filename"],
                os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
                os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
                HPARAMS["brain_username"],
                HPARAMS["brain_ip"],
            ),
        )
    # Batch 2: send mono image, move servos, record stereo video
    robot_log += "Adding record_video to tasks."
    task_batch.append(
        record_video(
            CAMERAS["stereo"],
            HPARAMS["video_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
            HPARAMS["video_duration"],
            HPARAMS["video_fps"],
        ),
    )
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    # Create new task batch
    task_batch = []
    # Sending video requires an error free capture
    robot_log += results[-1]["log"]
    if results[-1].get("output_path") is not None:
        robot_log += "Adding send_file to tasks."
        task_batch.append(
            send_file(
                HPARAMS["video_filename"],
                os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
                os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
                HPARAMS["brain_username"],
                HPARAMS["brain_ip"],
            ),
        )
    # Add any other results to robot log
    for result in results[:-1]:
        robot_log += result["log"]
    # Write robot log to file
    with open(HPARAMS["robotlog_filename"], "w") as f:
        f.write(robot_log)
    # Batch 3: send robot log, send stereo video, update ui
    task_batch.append(
        send_file(
            HPARAMS["robotlog_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
            os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
            HPARAMS["brain_username"],
            HPARAMS["brain_ip"],
        )
    )
    task_batch.append(
        ui.update_interface(),
    )
    results = await asyncio.gather(*task_batch, return_exceptions=True)


if __name__ == "__main__":
    HPARAMS["session_name"] = create_session_folder(HPARAMS["robot_data_dir"])
    servos = Servos()
    ui = ChromeUI()
    asyncio.run(main_loop(servos, ui))
