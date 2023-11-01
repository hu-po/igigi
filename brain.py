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
    print("Starting main loop")
    print("Batch 1 of tasks")
    results = await asyncio.gather(
        find_file(
            hparams.get("robotlog_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        find_file(
            hparams.get("image_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        return_exceptions=True,
    )
    print(results)
    print("Batch 2 of tasks")
    results = await asyncio.gather(
        run_vlm(
            hparams.get("vlm_prompt"),
            hparams.get("vlm_docker_url"),
            os.path.join(hparams.get("brain_data_dir"), hparams.get("image_filename")),
        ),
        return_exceptions=True,
    )
    print(results)
    print("Batch 3 of tasks")
    results = await asyncio.gather(
        send_file(
            hparams.get("commands_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("robot_data_dir"),
            hparams.get("robot_username"),
            hparams.get("robot_ip"),
        ),
        return_exceptions=True,
    )


if __name__ == "__main__":
    docker = VLMDocker()
    asyncio.run(main_loop())
