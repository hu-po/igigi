import asyncio
import os
import shutil

from hparams import HPARAMS
from utils import find_file, send_file, task_batch, write_log
from vlm import VLMDocker, run_vlm


def _loop():
    if os.path.exists(HPARAMS["brain_data_dir"]):
        shutil.rmtree(HPARAMS["brain_data_dir"])
    os.makedirs(HPARAMS["brain_data_dir"], exist_ok=True)
    _ = VLMDocker()
    # startup tasks
    tasks = [
        ("find_file", find_file("image", "brain")),
        ("find_file", find_file("brainlog", "brain", read=True)),
    ]
    while True:
        state = asyncio.run(task_batch(tasks, "brain"))
        # Reset tasks
        tasks = []
        # if log hasn't been saved in a while
        if state.get("brainlog_age", 0) > HPARAMS["brainlog_max_age"]:
            tasks.append(write_log(state["log"], "brain"))
        # always check for brainlog
        tasks.append(("find_file", find_file("brainlog", "brain", read=True)))
        # always check for image
        tasks.append(("find_file", find_file("image", "brain")))
        # if there is an image, run VLM
        if state.get("image_path", None) is not None:
            tasks.append(("run_vlm", run_vlm()))
        # if there is a VLM output, write and send
        if state.get("reply", None) is not None:
            _path = os.path.join(HPARAMS["brain_data_dir"], HPARAMS["vlmout_filename"])
            # TODO: check if path exists, if it is abve a certain size, delete it
            with open(_path, "w") as f:
                f.write(state["reply"])
            tasks.append(("send_file", send_file(HPARAMS["vlmout_filename"], "brain", "robot")))


if __name__ == "__main__":
    print("Starting brain main loop.")
    _loop()

