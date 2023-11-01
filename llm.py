from typing import Any, Dict

import openai

from hparams import HPARAMS
from utils import async_timeout
from servos import Servos

@async_timeout(timeout=HPARAMS["timeout_move_servos"])
async def move_servos(
    servos: Servos,
    system_prompt: str,
    commands_filename: str = HPARAMS["commands_filename"],
    model: str = HPARAMS["robot_llm_model"],
    temperature: int = HPARAMS["robot_llm_temperature"],
    max_tokens: int = HPARAMS["robot_llm_max_tokens"],
) -> Dict[str, Any]:
    for pose in servos.poses.values():
        system_prompt += f"{pose.name} : {pose.desc}\n"
    for move in servos.moves.values():
        system_prompt += f"{move.name} : {move.desc}\n"
    with open(commands_filename, "r") as f:
        user_prompt = f.read()
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
    return {
        "log": servolog,
        "reply": reply,
    }