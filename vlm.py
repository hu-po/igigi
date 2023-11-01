import os
import subprocess
import time
import base64
from typing import Any, Dict

from hparams import HPARAMS
from utils import async_timeout
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

@async_timeout(timeout=HPARAMS["timeout_run_vlm"])
async def run_vlm(prompt: str, docker_url: str, image_filepath: str) -> Dict[str, Any]:
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
        return {
            "log": f"Ran VLM with prompt {prompt} and image {image_filepath}.",
            "reply": ''.join(response.json()["output"]),
        }
