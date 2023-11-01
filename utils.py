import os
import asyncio
import time
import uuid
import random
from datetime import datetime
from typing import Callable, Any, Dict

from hparams import HPARAMS


def async_timeout(timeout: int):
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            try:
                log: str = f"Calling {func.__name__}."
                print(log)
                results = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                assert "log" in results.keys(), "Could not find log in {func.__name__}"
                return {"log": log + results["log"], **results}
            except asyncio.TimeoutError:
                return {
                    "log": log + f"Timeout after {timeout} seconds in {func.__name__}"
                }
            except Exception as e:
                return {"log": log + f"Exception {e} in {func.__name__}"}

        return wrapper

    return decorator


@async_timeout(timeout=HPARAMS["timeout_find_file"])
async def find_file(filename: str, directory: str, interval: float) -> Dict[str, Any]:
    while True:
        if filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            file_time = os.path.getmtime(full_path)
            file_age = time.time() - file_time
            return {
                "log": f"Found {filename}, last modified {file_age} seconds ago.",
                "full_path": full_path,
                "file_age": file_age,
            }
        await asyncio.sleep(interval)


@async_timeout(timeout=HPARAMS["timeout_send_file"])
async def send_file(
    filename: str,
    local_dir_path: str,
    remote_dir_path: str,
    remote_username: str,
    remote_ip: str,
) -> Dict[str, Any]:
    process = await asyncio.create_subprocess_exec(
        *[
            "scp",
            os.path.join(local_dir_path, filename),
            f"{remote_username}@{remote_ip}:{os.path.join(remote_dir_path, filename)}",
        ],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode == 0:
        return {"log": f"Sent {filename} to {remote_ip}."}
    else:
        return {"log": f"Error sending {filename} to {remote_ip}: {stderr.decode()}"}


def create_session_folder(
    base_dir: str,
    seed: int = HPARAMS["seed"],
    folder_stem: str = HPARAMS["folder_stem"],
    date_format: str = HPARAMS["date_format"],
) -> str:
    random.seed(seed)
    session_id = str(uuid.UUID(int=random.getrandbits(128)))[:6]
    current_date = datetime.now().strftime(date_format)
    folder_name = f"{folder_stem}.{session_id}.{current_date}"
    session_folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(session_folder_path, exist_ok=True)
    print(f"Created session folder {session_folder_path} for random seed {seed}.")
    return folder_name