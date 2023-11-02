import asyncio
import os
import shutil

from hparams import HPARAMS, Task
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
        Task("find_file", find_file("vlmout", "robot", read=True)),
        Task("find_file", find_file("robotlog", "robot", read=True)),
        Task("set_servos", set_servos("forward", servos)),
        Task("take_image", take_image(HPARAMS["cameras"]["stereo"])),
    ]
    while True:
        state = asyncio.run(task_batch(tasks, "robot"))
        # Reset tasks
        tasks = []
        # if log hasn't been saved in a while
        if state.get("robotlog_age", 0) > HPARAMS["robotlog_max_age"]:
            tasks.append(Task("write_log", write_log(state["log"], "robot")))
        # always check for brainlog
        tasks.append(Task("find_file", find_file("robotlog", "robot", read=True)))
        # always capture image
        tasks.append(Task("take_image", take_image(HPARAMS["cameras"]["stereo"])))
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
            tasks.append(Task("run_llm", run_llm(messages)))
        else:
            # try and find vlmouts if no vlmout
            tasks.append(Task("find_file", find_file("vlmout", "robot", read=True)))
        # always move
        if state.get("reply", None) is not None:
            # if action, move servos
            tasks.append(Task("set_servos", set_servos(state["reply"], servos)))

if __name__ == "__main__":
    print("Starting robot main loop.")
    _loop()
