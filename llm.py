from typing import Any, Dict

import openai

from hparams import HPARAMS
from utils import async_timeout
from servos import Servos


@async_timeout(timeout=HPARAMS["timeout_move_servos"])
async def run_llm(
    system: str,
    user: str,
    model: str = HPARAMS["robot_llm_model"],
    temperature: int = HPARAMS["robot_llm_temperature"],
    max_tokens: int = HPARAMS["robot_llm_max_tokens"],
) -> Dict[str, Any]:
    log: str = f"SYSTEM: {system}\n USER: {user}\n"
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    reply: str = response.choices[0].message.content
    log += f"REPLY: {reply}"
    return {
        "log": log,
        "reply": reply,
    }

def move(
    self,
    action: str,
    servos: Servos,
    epsilon: int = HPARAMS["move_servo_speed"],
    speed: int = HPARAMS["move_epsilon_degrees"],
    timeout: int = HPARAMS["move_timeout_seconds"],
    interval: float = HPARAMS["move_interval_seconds"],
) -> str:
    timeout: timedelta = timedelta(seconds=timeout)
    start_time = time.time()
    move_log: str = "" #f"Started action at {start_time}."
    # Check to see if action is one of the static poses
    desired_pose = self.poses.get(action, None)
    if desired_pose is not None:
        move_log += f"Action is moving to static position {desired_pose.name}"
        goal_position = desired_pose.angles
    else:
        # Check to see if action is one of the moves
        desired_move = self.moves.get(action, None)
        if desired_move is not None:
            move_log += f"Action is moving {desired_move.name}"
            move_vector = [x * speed for x in desired_move.vector]
            move_log += f"Move vector is {move_vector}."
            true_position = self._read_pos()
            goal_position = [move_vector[i] + true_position[i] for i in range(len(move_vector))]
        else:
            move_log += f"ERROR: Could not find a match for desired action {action}.\n"
            return move_log
    move_log += f"Goal position is {goal_position}."
    while True:
        self._write_position(goal_position)
        true_positions = self._read_pos()
        distance_to_target: int = sum(abs(true_positions[i] - goal_position[i]) for i in range(len(goal_position)))
        move_log += f"Distance to target is {distance_to_target}."
        if epsilon > distance_to_target:
            move_log += f"Action succeeded in {elapsed_time} seconds."
            break
        time.sleep(interval)
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout.total_seconds():
            move_log += f"Action timed out after {elapsed_time} seconds."
            break
    move_log += f"Current position is {self._read_pos()}."
    return move_log + "\n"

