import asyncio
import os
from typing import Any, Dict
import time

from hparams import HPARAMS
from utils import find_file, send_file, create_session_folder, async_timeout
from record import take_image, record_video, CAMERAS
from llm import run_llm
from servos import Servos
from app import ChromeUI


@async_timeout(timeout=HPARAMS["timeout_robot_main_loop"])
async def main_loop(servos: Servos, ui: ChromeUI) -> Dict[str, Any]:
    print("Starting main loop.")
    log: str = ""
    # Batch 1: get commands, take mono image
    task_batch = [
        find_file(
            HPARAMS["commands_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
            HPARAMS["find_file_interval"],
        ),
        take_image(
            CAMERAS["stereo"],
            HPARAMS["image_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
        ),
    ]
    print(f"Run task_batch 1, {len(task_batch)} tasks.")
    start_time = time.time()
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    print(f"task_batch 1 took {time.time() - start_time} seconds.")
    for result in results:
        log += result["log"]
    task_batch = []
    # Moving servos requires a commands file
    # Once there is a command file then you can create an llm job
    # The crafting of the llm command prompt and checking whether
    # the llm job runs on batch 2, the move runs on batch 1 if the file is found
    # its more about creating this type of task queue where snakes of tasks
    # can be added. Like a chain of tasks. (for the next X moves do this chain of tasks, if there are issues, re-put the task on the queue, if a certain amount of fails exceed then you can stop)
    if results[0].get("full_path", None) is None:
        log += "No command file found."
    elif results[0]["file_age"] > HPARAMS["commands_max_age"]:
        log += "Command file is too old."
    else:
        log += "Adding move_servos to tasks."
        with open(results[0]["full_path"], "r") as f:
            commands = f.read()
        # Add moves and poses to commands
        prompt: str = HPARAMS["robot_llm_system_prompt"]
        for move in HPARAMS["moves"].values():
            prompt += f"{move.name}: {move.desc}\n"
        for pose in HPARAMS["poses"].values():
            prompt += f"{pose.name}: {pose.desc}\n"
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": commands},
        ]
        log += f"SYSTEM: {prompt}"
        log += f"USER: {commands}"
        print(f"Commands: {commands}")
        task_batch.append(
            run_llm(
                messages,
                HPARAMS["robot_llm_model"],
                HPARAMS["robot_llm_temperature"],
                HPARAMS["robot_llm_max_tokens"],
            ),
        )
    # Sending image requires an error free image capture
    if results[1].get("output_path") is not None:
        log += "Adding send_file to tasks."
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
    log += "Adding record_video to tasks."
    task_batch.append(
        record_video(
            CAMERAS["stereo"],
            HPARAMS["video_filename"],
            os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
            HPARAMS["video_duration"],
            HPARAMS["video_fps"],
        ),
    )
    print(f"Run task_batch 2, {len(task_batch)} tasks.")
    start_time = time.time()
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    print(f"task_batch 2 took {time.time() - start_time} seconds.")
    for result in results:
        log += result["log"]
    task_batch = []
    # Sending video requires an error free capture
    if results[-1].get("output_path") is not None:
        log += "Adding send_file to tasks."
        task_batch.append(
            send_file(
                HPARAMS["video_filename"],
                os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
                os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
                HPARAMS["brain_username"],
                HPARAMS["brain_ip"],
            ),
        )
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
    print(f"Run task_batch 3, {len(task_batch)} tasks.")
    start_time = time.time()
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    print(f"task_batch 3 took {time.time() - start_time} seconds.")
    for result in results:
        log += result["log"]
    return {"log": log}


if __name__ == "__main__":
    HPARAMS["session_name"] = create_session_folder(HPARAMS["robot_data_dir"])
    # Robot is a singleton, requires state, start it in home position
    servos = Servos()
    servos.move("home")
    ui = ChromeUI(
        os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
        HPARAMS.get("video_filename"),
        HPARAMS.get("image_filename"),
        HPARAMS.get("robotlog_filename"),
    )
    while True:
        result = asyncio.run(main_loop(servos, ui))
        print(result["log"])
        output_path = os.path.join(
            HPARAMS["robot_data_dir"],
            HPARAMS["session_name"],
            HPARAMS["robotlog_filename"],
        )
        with open(output_path, "w") as f:
            f.write(result["log"])
