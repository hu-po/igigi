from typing import Any, Dict

import openai
import time
from datetime import timedelta
from typing import Any, Dict, List

from hparams import HPARAMS, Pose, Move
from utils import async_task
from servos import Servos


@async_task(timeout=HPARAMS["timeout_run_llm"])
async def run_llm(
    messages: List[Dict[str, str]],
    model: str = HPARAMS["robot_llm_model"],
    temperature: int = HPARAMS["robot_llm_temperature"],
    max_tokens: int = HPARAMS["robot_llm_max_tokens"],
) -> Dict[str, Any]:
    log: str = f"Calling LLM with messages {messages}."
    response = openai.ChatCompletion.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    reply: str = response.choices[0].message.content
    log += f"LLM: {reply}"
    return {
        "log": log,
        "reply": reply,
    }

@async_task(timeout=HPARAMS["timeout_move_servos"])
async def movement_action(
    action: str,
    servos: Servos,
    pose_dict: Dict[str, Pose] = HPARAMS["poses"],
    move_dict: Dict[str, Move] = HPARAMS["moves"],
    speed: int = HPARAMS["move_speed"],
    duration: int = HPARAMS["move_duration"],
    interval: float = HPARAMS["move_interval"],
) -> Dict[str, Any]:
    log: str = f"Action {action}."
    # Pick the goal position
    desired_pose = pose_dict.get(action, None)
    if desired_pose is not None:
        log += "is a Pose."
        goal_pos = desired_pose.angles
    else:
        desired_move = move_dict.get(action, None)
        if desired_move is not None:
            log += "is a Move."
            move_vector = [x * speed for x in desired_move.vector]
            log += f"Move vector is {move_vector}."
            true_pos = servos._read_pos()
            goal_pos = [move_vector[i] + true_pos[i] for i in range(len(move_vector))]
        else:
            log += "is not valid. Moving to home position."
            goal_pos = pose_dict["home"].angles
    log += f"Goal position is {goal_pos}."
    # Move to the goal position over timeout seconds
    duration: timedelta = timedelta(seconds=duration)
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration.total_seconds():
            log += f"Action finished after {elapsed_time} seconds."
            break
        true_pos = servos._read_pos()
        # Interpolate between the current position and the goal position
        # based on the fraction of time elapsed
        fraction = elapsed_time / duration.total_seconds()
        interpolated_position = [
            int((goal_pos[i] - true_pos[i]) * fraction + true_pos[i])
            for i in range(len(goal_pos))
        ]
        servos._write_position(interpolated_position)
        distance_to_target: int = sum(abs(true_pos[i] - goal_pos[i]) for i in range(len(goal_pos)))
        log += f"Distance to target is {distance_to_target}."
        time.sleep(interval)
    true_pos = servos._read_pos()
    log += f"Current position is {true_pos}."
    return {
        "log": log,
        "pos": true_pos,
    }

