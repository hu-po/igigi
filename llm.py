import openai
from typing import Any, Dict, List

from hparams import HPARAMS

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
    return {"log": log, "reply": reply}