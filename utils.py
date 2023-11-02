import os
import asyncio
import time
import pprint
from typing import Callable, Any, Dict

from hparams import HPARAMS


def async_task(timeout: int):
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            try:
                out: Dict[str, Any] = {"log": f"Calling {func.__name__}."}
                print(out["log"])
                start_time = time.time()
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                duration = time.time() - start_time
                out["log"] += f"Completed after {duration} seconds."
                print(out["log"])
                for name, value in result.items():
                    if name == "log":
                        out["log"] += result["log"]
                    else:
                        out[name] = value
            except asyncio.TimeoutError:
                out["log"] += f"Timeout after {timeout} seconds."
            except Exception as e:
                out["log"] += f"Exception {e}"
            return out

        return wrapper

    return decorator


async def task_batch(task_batch) -> Dict[str, Any]:
    print("\n\nNew Task Batch")
    if len(task_batch) == 0:
        log: str = "No tasks to run."
        return {"log": log}
    out: Dict[str, Any] = {"log": f"Running batch of {len(task_batch)} tasks."}
    results = await asyncio.gather(*task_batch, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            continue
        for name, value in result.items():
            if name == "log":
                out["log"] += result["log"]
            else:
                out[name] = value
    pprint(out["log"])
    return out


@async_task(timeout=HPARAMS["timeout_find_file"])
async def find_file(
    retkey: str,
    filename: str,
    directory: str,
    interval: float = HPARAMS["find_file_interval"],
    open: bool = False,
) -> Dict[str, Any]:
    while True:
        if filename in os.listdir(directory):
            out: Dict[str, Any] = {"log" : f"Found {filename}."}
            full_path = os.path.join(directory, filename)
            file_time = os.path.getmtime(full_path)
            file_age = time.time() - file_time
            out[f"{retkey}_path"] = full_path
            out[f"{retkey}_age"] = file_age
            if open:
                with open(full_path, "r") as f:
                    out[retkey] = f.read()
            return out
        await asyncio.sleep(interval)
    


@async_task(timeout=HPARAMS["timeout_send_file"])
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
