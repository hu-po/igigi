import asyncio
import os
from typing import Any, Dict
import time

from hparams import HPARAMS
from utils import find_file, send_file, task_batch
from record import take_image
from llm import run_llm, movement_action
from servos import Servos
from app import ChromeUI


def _loop():
    os.makedirs(HPARAMS["robot_data_dir"], exist_ok=True)
    # Robot is a singleton, requires state, start it in home position
    servos = Servos()
    # ui = ChromeUI()
    tasks = [
        find_file("command", HPARAMS["rawaction_filename"], HPARAMS["robot_data_dir"], open=True),
        movement_action("home", servos),
        take_image(HPARAMS["cameras"]["stereo"]),
    ]
    while True:
        state = asyncio.run(task_batch(tasks))
        # Write logs to file
        _path = os.path.join(HPARAMS["robot_data_dir"], HPARAMS["robotlog_filename"])
        with open(_path, "a") as f:
            f.write(state["log"])
        # Reset tasks
        tasks = []
        # always capture image
        tasks.append(take_image(HPARAMS["cameras"]["stereo"]))
        # if image, send it to brain
        if state.get("image_output_path", None) is not None:
            tasks.append(send_file(
                HPARAMS["image_filename"],
                HPARAMS["robot_data_dir"],
                HPARAMS["brain_data_dir"],
                HPARAMS["brain_username"],
                HPARAMS["brain_ip"],
            ))
        # # if video, send it to vizzy
        # if state.get("video_output_path", None) is not None:
        #     tasks.append(send_file(
        #         HPARAMS["image_filename"],
        #         HPARAMS["robot_data_dir"],
        #         HPARAMS["vizzy_data_dir"],
        #         HPARAMS["vizzy_ip"],
        #         HPARAMS["vizzy_username"],
        #     ))
        # if commands, call llm
        if state.get("command", None) is not None:
            # Add moves and poses to commands
            prompt: str = HPARAMS["robot_llm_system_prompt"]
            for name, move in HPARAMS["moves"].items():
                prompt += f"{name}: {move.desc}\n"
            for name, pose in HPARAMS["poses"].items():
                prompt += f"{name}: {pose.desc}\n"
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": state["commands"]},
            ]
            tasks.append(run_llm(messages))
        else:
            # try and find commands if no command
            tasks.append(find_file("command", HPARAMS["rawaction_filename"], HPARAMS["robot_data_dir"], open=True))
        # always move
        if state.get("action", None) is not None:
            # if action, move servos
            tasks.append(movement_action(state["command"], servos))
        else:
            # if no action, move to home position
            tasks.append(movement_action("home", servos))


if __name__ == "__main__":
    print("Starting robot main loop.")
    _loop()
