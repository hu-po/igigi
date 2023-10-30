import asyncio
import os
import sys
import subprocess
import time
import base64

# from .utils import scrape_callback, send_file
from hparams import HPARAMS
import requests
# from PIL import Image

class MiniDocker:

    def __init__(self, name: str = 'llava13b', port: str = '5000', warmup: int = 30):
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
            os.system(f"docker kill {containers}")
            os.system(f"docker stop {containers}")
            os.system(f"docker rm {containers}")
        os.system("docker container prune -f")

    def __del__(self):
        self.proc.terminate()
        self.nuke()


async def run_vlm(
    docker: MiniDocker,
    brain_data_dir: str,
    input_image_path: str,
    vlm_log_filename: str,
    prompt: str = "Is there a person in this image? Where are they? On the left? right? center?",
    fps: int = 30,
    docker_url: str = "http://localhost:5000/predictions",
    **kwargs,
):
    """
# https://replicate.com/yorickvp/llava-13b
docker run --name llava13b r8.im/yorickvp/llava-13b@sha256:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591
docker commit llava13b llava13b
# Use weights stored locally (also needs to download clip336)
docker run -v /home/oop/dev/LLaVA/llava-v1.5-13b:/src/liuhaotian/llava-v1.5-13b --gpus=all llava13b
docker commit llava13b llava13b

    """
    image_path = os.path.join(brain_data_dir, input_image_path)
    with open(image_path, "rb") as img_file:
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
        time.sleep(10)
        return response.json()


async def main_loop(hparams: dict = HPARAMS):

    # # Generate a unique id for this generation session
    # session_id = str(uuid.uuid4())[:6]

    # # Create a output folder for the session id and use that as the output dir
    # output_dir = os.path.join(brain_data_dir, session_id)
    # os.makedirs(output_dir, exist_ok=True)


    # scrape for image + image log

    # scrape for servo + servo log

    # results = await asyncio.gather(*_tasks, return_exceptions=True)

    # # ask VLM for commands

    # results = await asyncio.gather(*_tasks, return_exceptions=True)
    
    # # write commands, send commands

    # results = await asyncio.gather(*_tasks, return_exceptions=True)

    pass

async def test(hparams: dict = HPARAMS):

    pass


if __name__ == "__main__":
    docker = MiniDocker()
    asyncio.run(main_loop(docker))
    del docker
    print("done")
