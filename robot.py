import asyncio
import os

from openai import OpenAI


from .hparams import HPARAMS
from .utils import scrape, send_file
from .record import take_image, record_video, CAMERAS
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
    servolog = servos.move(reply)
    return servolog


async def main_loop(servos: Servos, llm, hparams: dict = HPARAMS):
    results = await asyncio.gather(
        scrape(
            hparams.get("commands_filename"),
            hparams.get("brain_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        take_image(
            CAMERAS["stereo"],
            hparams.get("image_filename"),
            hparams.get("robot_data_path"),
        ),
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
        move_servos(
            servos, llm,
            hparams.get("llm_system_prompt"),
            hparams.get("llm_move_prompt"),
            hparams.get("llm_model"),
            hparams.get("llm_temperature"),
            hparams.get("llm_max_tokens"),
        ),
        record_video(
            CAMERAS["stereo"],
            hparams.get("video_filename"),
            hparams.get("robot_data_path"),
            hparams.get("video_duration"),
            hparams.get("video_fps"),
        ),
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
