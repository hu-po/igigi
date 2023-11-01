import asyncio
import os
import subprocess
import time
import base64

from hparams import HPARAMS
from utils import find_file, send_file
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
    return_exceptions=True)
    print(results)
    print("Batch 2 of tasks")
    results = await asyncio.gather(
        run_vlm(
            hparams.get("vlm_prompt"),
            hparams.get("vlm_docker_url"),
            os.path.join(hparams.get("brain_data_dir"), hparams.get("image_filename")),
        ),
    return_exceptions=True)
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
    return_exceptions=True)

if __name__ == "__main__":
    docker = VLMDocker()
    asyncio.run(main_loop())
