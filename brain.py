import asyncio
import os

from hparams import HPARAMS
from utils import find_file, send_file, task_batch
from vlm import VLMDocker, run_vlm


def _loop():
    os.makedirs(HPARAMS["brain_data_dir"], exist_ok=True)
    _ = VLMDocker()
    # startup tasks
    tasks = [find_file("image", HPARAMS["image_filename"], HPARAMS["brain_data_dir"])]
    while True:
        state = asyncio.run(task_batch(tasks))
        # Write logs to file
        _path = os.path.join(HPARAMS["brain_data_dir"], HPARAMS["brainlog_filename"])
        with open(_path, "a") as f:
            f.write(state["log"])
        # Reset tasks
        tasks = []
        # always check for image
        tasks.append(find_file("image", HPARAMS["image_filename"], HPARAMS["brain_data_dir"]))
        # if there is an image, run VLM
        if state.get("image_path", None) is not None:
            tasks.append(run_vlm())
        # if there is a VLM output, write and send
        if state.get("reply", None) is not None:
            command_path = os.path.join(HPARAMS["brain_data_dir"], HPARAMS["commands_filename"])
            with open(command_path, "w") as f:
                f.write(state["reply"])
            tasks.append(send_file(
                HPARAMS["commands_filename"],
                HPARAMS["brain_data_dir"],
                HPARAMS["robot_data_dir"],
                HPARAMS["robot_username"],
                HPARAMS["robot_ip"],
            ))


if __name__ == "__main__":
    print("Starting brain main loop.")
    _loop()

