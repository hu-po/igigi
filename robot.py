import asyncio
import os
import shutil

from hparams import HPARAMS
from utils import find_file, send_file, task_batch, write_log
from record import take_image
from llm import run_llm
from servos import Servos, set_servos


def _loop():
    if os.path.exists(HPARAMS["robot_data_dir"]):
        shutil.rmtree(HPARAMS["robot_data_dir"])
    os.makedirs(HPARAMS["robot_data_dir"], exist_ok=True)
    # Robot is a singleton, requires state
    servos = Servos()
    tasks = [
        find_file("vlmout", HPARAMS["vlmout_filename"], HPARAMS["robot_data_dir"], read=True),
        find_file("robotlog", HPARAMS["robotlog_filename"], HPARAMS["robot_data_dir"], read=True),
        set_servos("forward", servos),
        take_image(HPARAMS["cameras"]["stereo"]),
    ]
    while True:
        state = asyncio.run(task_batch(tasks))
        # Reset tasks
        tasks = []
        # if log hasn't been saved in a while
        if state.get("robotlog_age", 0) > HPARAMS["robotlog_max_age"]:
            tasks.append(write_log(
                state["log"],
                HPARAMS["robotlog_filename"],
                HPARAMS["robot_data_dir"],
            ))
        # always check for brainlog
        tasks.append(find_file("robotlog", HPARAMS["brainlog_filename"], HPARAMS["brain_data_dir"], read=True))
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
        # # if video, send it to viewr
        # if state.get("video_output_path", None) is not None:
        #     tasks.append(send_file(
        #         HPARAMS["image_filename"],
        #         HPARAMS["robot_data_dir"],
        #         HPARAMS["viewr_data_dir"],
        #         HPARAMS["viewr_ip"],
        #         HPARAMS["viewr_username"],
        #     ))
        # if vlmouts, call llm
        if state.get("vlmout", None) is not None:
            # Add moves and poses to vlmouts
            prompt: str = HPARAMS["robot_llm_prompt"]
            for name, move in HPARAMS["moves"].items():
                prompt += f"{name}: {move.desc}\n"
            for name, pose in HPARAMS["poses"].items():
                prompt += f"{name}: {pose.desc}\n"
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": state["vlmout"]},
            ]
            tasks.append(run_llm(messages))
        else:
            # try and find vlmouts if no vlmout
            tasks.append(find_file("vlmout", HPARAMS["vlmout_filename"], HPARAMS["robot_data_dir"], read=True))
        # always move
        if state.get("reply", None) is not None:
            # if action, move servos
            tasks.append(set_servos(state["reply"], servos))
        # else:
        #     # if no action, move to forward position
        #     tasks.append(servo_action("forward", servos))


if __name__ == "__main__":
    print("Starting robot main loop.")
    _loop()
