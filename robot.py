import asyncio
import os
import shutil

from hparams import HPARAMS, Task
from utils import find_file, send_file, task_batch, write_log, clear_data
from llm import run_llm
from cam import OpenCVCam
from servos import Servos


def _loop():
    servos = Servos()
    camera = OpenCVCam()
    tasks = [
        Task("clear_data", clear_data("robot")),
        Task("set_servos", servos.set_servos("forward", servos)),
        Task("take_image", camera.take_image()),
    ]
    state = asyncio.run(task_batch(tasks, "robot", ordered=True))
    while True:
        state = asyncio.run(task_batch(tasks, "robot"))
        # Reset task
        tasks = []
        # if log hasn't been saved in a while
        if state.get("robotlog_age", 0) > HPARAMS["robotlog_max_age"] or state.get("robotlog", None) is None:
            tasks.append(Task("write_log", write_log(state["log"], "robot")))
        # always check for brainlog
        tasks.append(Task("find_file", find_file("robotlog", "robot", read=True)))
        # always capture image
        tasks.append(Task("take_image", camera.take_image()))
        # if image, send it to brain
        if state.get("image_output_path", None) is not None:
            tasks.append(Task("send_file", send_file("image", "robot", "brain")))
        # TODO: if video, send it to viewr
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
            tasks.append(Task("run_llm", run_llm(messages), HPARAMS["robot_llm_timeout"]))
        else:
            # try and find vlmouts if no vlmout
            tasks.append(Task("find_file", find_file("vlmout", "robot", read=True)))
        # always move
        if state.get("reply", None) is not None:
            # if action, move servos
            tasks.append(Task("set_servos", servos.set_servos(state["reply"], servos)))

if __name__ == "__main__":
    print("Starting robot main loop.")
    _loop()
