import os
import asyncio
import time
from pprint import pprint
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
    pprint(out)
    return out


@async_task(timeout=HPARAMS["timeout_find_file"])
async def find_file(
    retkey: str,
    filename: str,
    node_name: str,
    interval: float = HPARAMS["find_file_interval"],
    read: bool = False,
) -> Dict[str, Any]:
    directory: str = HPARAMS[f"{node_name}_data_dir"]
    node_token: str = HPARAMS[f"{node_name}_token"]
    out: Dict[str, Any] = {"log": f"{HPARAMS['find_token']} looking for {filename} in {node_token}"}
    while True:
        if filename in os.listdir(directory):
            out["log"] += "... found"
            full_path = os.path.join(directory, filename)
            file_time = os.path.getmtime(full_path)
            file_age = time.time() - file_time
            out["log"] += f" last modified {file_age}s ago"
            out[f"{retkey}_path"] = full_path
            out[f"{retkey}_age"] = file_age
            if read:
                with open(full_path, "r") as f:
                    out[retkey] = f.read()
            break
        await asyncio.sleep(interval)
    out["log"] += "\n"
    return out


@async_task(timeout=HPARAMS["timeout_send_file"])
async def send_file(
    filename: str,
    local_name: str = HPARAMS["robot_username"],
    remote_name: str = HPARAMS["brain_username"],
) -> dict:
    local_dir_path: str = HPARAMS[f"{local_name}_data_dir"]
    remote_dir_path: str = HPARAMS[f"{remote_name}_data_dir"]
    remote_username: str = HPARAMS[f"{remote_name}_username"]
    remote_ip: str = HPARAMS[f"{remote_name}_ip"]
    local_token = HPARAMS[f"{local_name}_token"]
    remote_token = HPARAMS[f"{remote_name}_token"]
    out: dict = {"log": f"{HPARAMS['send_token']} sending {filename} from {local_token} to {remote_token}"}
    cmd = [
        "/usr/bin/scp",
        os.path.join(local_dir_path, filename),
        f"{remote_username}@{remote_ip}:{os.path.join(remote_dir_path, filename)}",
    ]
    result = os.system(" ".join(cmd))
    if result != 0:
        out["log"] += "... failed"
    out["log"] += "\n"
    return out


@async_task(timeout=HPARAMS["timeout_write_log"])
async def write_log(
    log: str,
    filename: str,
    directory: str,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {"log": f"{HPARAMS['save_token']} saving logs {filename}"}
    full_path = os.path.join(directory, filename)
    with open(full_path, "a") as f:
        f.write(log)
    out["log"] += "\n"
    return out