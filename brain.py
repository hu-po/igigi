import asyncio
import os
import sys
import subprocess
import time
import base64
import uuid

from .utils import scrape, send_file
from hparams import HPARAMS
import requests

class VLMDocker:

    def __init__(self, name: str = 'llava13b', port: str = '5000', warmup: int = 25):
        self.nuke()
        self.name, self.port, self.warmup = name, port, warmup
        self.proc = subprocess.Popen([
            "docker", "run", "--rm", 
            "-v", "/home/oop/dev/LLaVA/llava-v1.5-13b:/src/liuhaotian/llava-v1.5-13b", 
            "-p", f"{port}:{port}", 
            "--gpus=all", 
            name
        ])
        time.sleep(self.warmup)

    def nuke(self):
        containers = os.popen("docker ps -aq").read().strip()
        if containers:
            os.system(f"docker stop {containers}")
            os.system(f"docker kill {containers}")
            os.system(f"docker rm {containers}")
        os.system("docker container prune -f")

    def __del__(self):
        self.proc.terminate()
        self.nuke()


async def run_vlm(prompt: str, docker_url: str, image_filepath: str):
    with open(image_filepath, "rb") as img_file:
        response = requests.post(
            docker_url,
            headers={"Content-Type": "application/json"},
            json={
                "input": {
                    "image": f"data:image/png;base64,{base64.b64encode(img_file.read()).decode('utf-8')}",
                    "prompt": prompt,
                },
            },
        )
        return ''.join(response.json()["output"])


async def main_loop(hparams: dict = HPARAMS):

    results = await asyncio.gather(
        scrape(
            hparams.get("robotlog_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        scrape(
            hparams.get("image_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        return_exceptions=True,
    )

    # # ask VLM for commands
    vlm_results = await asyncio.gather(
        run_vlm(
            hparams.get("vlm_prompt"),
            hparams.get("vlm_docker_url"),
            os.path.join(hparams.get("brain_data_dir"), hparams.get("image_filename")),
        ),
    return_exceptions=True)

    # write commands to file

    # send commands to robot
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
