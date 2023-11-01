import asyncio
import os

from hparams import HPARAMS
from utils import find_file, send_file
from vlm import VLMDocker, run_vlm


async def main_loop(hparams: dict = HPARAMS):
    """
    the following this is a set of asynchronous functions
    some functions require the output of other functions
    based on previous history you must select one of these functions
    the functions are

    the history is
    """
    # Batch 1: get robot log, get mono image
    task_batch = [
        find_file(
            HPARAMS["robotlog_filename"],
            HPARAMS["brain_data_dir"],
            HPARAMS["scrape_interval"],
            HPARAMS["scrape_timeout"],
        ),
        find_file(
            HPARAMS["image_filename"],
            HPARAMS["brain_data_dir"],
            HPARAMS["scrape_interval"],
            HPARAMS["scrape_timeout"],
        ),
    ]
    results = await asyncio.gather(*task_batch, return_exceptions=True)

    # Batch 2: run vlm
    task_batch = [
        run_vlm(
            HPARAMS["vlm_prompt"],
            HPARAMS["vlm_docker_url"],
            os.path.join(HPARAMS["brain_data_dir"], HPARAMS["image_filename"]),
        ),
    ]
    results = await asyncio.gather(*task_batch, return_exceptions=True)

    # Batch 3: send commands
    task_batch = [
        send_file(
            HPARAMS["commands_filename"],
            HPARAMS["brain_data_dir"],
            HPARAMS["robot_data_dir"],
            HPARAMS["robot_username"],
            HPARAMS["robot_ip"],
        ),
    ]
    results = await asyncio.gather(*task_batch, return_exceptions=True)


if __name__ == "__main__":
    docker = VLMDocker()
    asyncio.run(main_loop())
