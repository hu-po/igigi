from typing import Any, Dict

import openai

from hparams import HPARAMS
from utils import async_timeout
from servos import Servos


@async_timeout(timeout=HPARAMS["timeout_move_servos"])
async def move_servos(
    servos: Servos,
    system_prompt: str,
    commands: str,
    model: str = HPARAMS["robot_llm_model"],
    temperature: int = HPARAMS["robot_llm_temperature"],
    max_tokens: int = HPARAMS["robot_llm_max_tokens"],
) -> Dict[str, Any]:
    for pose in servos.poses.values():
        system_prompt += f"{pose.name} : static pose, {pose.desc}\n"
    for move in servos.moves.values():
        system_prompt += f"{move.name} : movement, {move.desc}\n"
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": commands},
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    reply: str = response.choices[0].message.content
    print(f"LLM says: {reply}")
    servolog = servos.move(
        reply,
        speed=HPARAMS["move_servo_speed"],
        epsilon=HPARAMS["move_epsilon_degrees"],
        timeout=HPARAMS["move_timeout_seconds"],
        interval=HPARAMS["move_interval_seconds"],
    )
    return {
        "log": servolog,
        "reply": reply,
    }
