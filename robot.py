import asyncio
import os
import sys

from openai import OpenAI


from .hparams import HPARAMS
from .utils import scrape, send_file
from .record import take_image, record_video
from .servos import Servos


async def move_servos(
    servos: Servos,
    llm,
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: int = 0.2,
    max_tokens: int = 32,
) -> str:
    response = llm.chat_completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    reply: str = response.choices[0].message.content
    # desired_pose = POSES.get(desired_pose_name, None)
    # if desired_pose is not None:
    #     return servos.move(desired_pose.angles)
    # else:
    #     msg += f"ERROR: {desired_pose_name} is not a valid pose.\n"
    #     return msg


async def main_loop(servos: Servos, llm, hparams: dict = HPARAMS):
    results = await asyncio.gather(
        scrape(
            hparams.get("commands_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        take_image(),
        return_exceptions=True,
    )

    results = await asyncio.gather(
        send_file(
            hparams.get("image_filename"),
            hparams.get("robot_data_path"),
            hparams.get("brain_data_path"),
            hparams.get("brain_username"),
            hparams.get("brain_ip"),
        ),
        move_servos(servos, llm),
        record_video(),
        return_exceptions=True,
    )

    results = await asyncio.gather(
        send_file(
            hparams.get("video_filename"),
            hparams.get("robot_data_path"),
            hparams.get("brain_data_path"),
            hparams.get("brain_username"),
            hparams.get("brain_ip"),
        ),
        send_file(
            hparams.get("robot_log_filename"),
            hparams.get("robot_data_path"),
            hparams.get("brain_data_path"),
            hparams.get("brain_username"),
            hparams.get("brain_ip"),
        ),
        return_exceptions=True,
    )


if __name__ == "__main__":
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    servos = Servos()
    asyncio.run(main_loop(servos, llm))
