import asyncio
import os
from typing import Any, Dict

from hparams import HPARAMS
from utils import find_file, send_file, create_session_folder, async_timeout
from vlm import VLMDocker, run_vlm


@async_timeout(timeout=HPARAMS["timeout_brain_main_loop"])
async def main_loop() -> Dict[str, Any]:
    print("Starting main loop.")
    log: str = ""
    # Batch 1: get robot log, get mono image
    task_batch = [
        find_file(
            HPARAMS["robotlog_filename"],
            os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
            HPARAMS["find_file_interval"],
        ),
        find_file(
            HPARAMS["image_filename"],
            os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
            HPARAMS["find_file_interval"],
        ),
    ]
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    for result in results:
        log += result["log"]
    task_batch = []
    # Executing VLM requires an image
    if results[0].get("full_path", None) is None:
        log += "No image found."
    elif results[0]["file_age"] > HPARAMS["image_max_age"]:
        log += "Image is too old."
    else:
        log += "Adding run_vlm to tasks."
        task_batch.append(
            run_vlm(
                HPARAMS["vlm_prompt"],
                HPARAMS["vlm_docker_url"],
                os.path.join(
                    HPARAMS["brain_data_dir"],
                    HPARAMS["session_name"],
                    HPARAMS["image_filename"],
                ),
            )
        )
    if len(task_batch) == 0:
        return {"log": log}
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    for result in results:
        log += result["log"]
    task_batch = []
    commands = results[0].get("reply", None)
    print(f"VLM says: {commands}")
    if commands is None:
        log += "No commands from VLM."
    else:
        with open(
            os.path.join(
                HPARAMS["brain_data_dir"],
                HPARAMS["session_name"],
                HPARAMS["commands_filename"],
            ),
            "w",
        ) as f:
            f.write(commands)
        log += "Adding send_file to tasks."
        task_batch.append(
            send_file(
                HPARAMS["commands_filename"],
                os.path.join(HPARAMS["brain_data_dir"], HPARAMS["session_name"]),
                os.path.join(HPARAMS["robot_data_dir"], HPARAMS["session_name"]),
                HPARAMS["robot_username"],
                HPARAMS["robot_ip"],
            ),
        )
    if len(task_batch) == 0:
        return {"log": log}
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    for result in results:
        log += result["log"]
    return {"log": log}


if __name__ == "__main__":
    HPARAMS["session_name"] = create_session_folder(HPARAMS["brain_data_dir"])
    docker = VLMDocker()
    while True:
        result = asyncio.run(main_loop())
        print(result["log"])
        output_path = os.path.join(
            HPARAMS["brain_data_dir"],
            HPARAMS["session_name"],
            HPARAMS["brainlog_filename"],
        )
        with open(output_path, "w") as f:
            f.write(result["log"])

