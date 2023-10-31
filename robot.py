import asyncio

import openai

from hparams import HPARAMS
from utils import scrape, send_file
from record import take_image, record_video, CAMERAS
from servos import Servos


async def move_servos(
    servos: Servos,
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: int = 0.2,
    max_tokens: int = 32,
) -> str:
    print(f"Moving servos with {user_prompt}")
    # Add actions to the system prompt
    for pose in servos.poses:
        system_prompt += f"{pose.name} : {pose.desc}\n"
    for move in servos.moves:
        system_prompt += f"{move.name} : {move.desc}\n"
    response = openai.ChatCompletion.create(
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


async def main_loop(servos: Servos, hparams: dict = HPARAMS):
    print("Starting main loop")
    print("Batch 1 of tasks")
    results = await asyncio.gather(
        scrape(
            hparams.get("commands_filename"),
            hparams.get("robot_data_dir"),
            hparams.get("scrape_interval"),
            hparams.get("scrape_timeout"),
        ),
        take_image(
            CAMERAS["stereo"],
            hparams.get("image_filename"),
            hparams.get("robot_data_dir"),
        ),
        return_exceptions=True,
    )
    print(results)
    print("Batch 2 of tasks")
    results = await asyncio.gather(
        send_file(
            hparams.get("image_filename"),
            hparams.get("robot_data_dir"),
            hparams.get("brain_data_dir"),
            hparams.get("brain_username"),
            hparams.get("brain_ip"),
        ),
        move_servos(
            servos,
            hparams.get("robot_llm_system_prompt"),
            "go to home position",
            hparams.get("robot_llm_model"),
            hparams.get("robot_llm_temperature"),
            hparams.get("robot_llm_max_tokens"),
        ),
        record_video(
            CAMERAS["stereo"],
            hparams.get("video_filename"),
            hparams.get("robot_data_dir"),
            hparams.get("video_duration"),
            hparams.get("video_fps"),
        ),
        return_exceptions=True,
    )
    print(results)
    print("Batch 3 of tasks")
    results = await asyncio.gather(
        send_file(
            hparams.get("robotlog_filename"),
            hparams.get("robot_data_dir"),
            hparams.get("brain_data_dir"),
            hparams.get("brain_username"),
            hparams.get("brain_ip"),
        ),
        # send_file(
        #     hparams.get("video_filename"),
        #     hparams.get("robot_data_dir"),
        #     hparams.get("brain_data_dir"),
        #     hparams.get("brain_username"),
        #     hparams.get("brain_ip"),
        # ),
        # update_ui(),
        return_exceptions=True,
    )


if __name__ == "__main__":
    servos = Servos()
    asyncio.run(main_loop(servos))
