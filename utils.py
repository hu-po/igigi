import os
import asyncio
import time
from typing import Any, Dict, List

from hparams import HPARAMS, Task


async def time_it(task: Task) -> Dict[str, Any]:
    prefix = f"{HPARAMS['time_token']} started {task.name} at {time.strftime(HPARAMS['time_format'])}"
    print(prefix)
    start_time = time.time()
    
    try:
        result = await asyncio.wait_for(task.coro, timeout=task.timeout)
    except asyncio.TimeoutError:
        suffix = f"{HPARAMS['time_token']} {HPARAMS['fail_token']} timedout {task.name} at {time.strftime(HPARAMS['time_format'])}"
    else:
        suffix = f"{HPARAMS['time_token']} finished {task.name} at {time.strftime(HPARAMS['time_format'])}"
    finally:
        elapsed_time = time.time() - start_time
        suffix += f" took {elapsed_time:.2f}s"
        print(suffix)
    result["log"] = f"{prefix}\n{result['log']}\n{suffix}"
    return result

async def task_batch(task_batch: List[Task], node_name: str) -> Dict[str, Any]:
    node_token: str = HPARAMS[f"{node_name}_token"]
    if len(task_batch) == 0:
        log: str = f"{node_token} no tasks to run."
        print(log)
        return {"log": log}
    prefix: str = f"{node_token} started batch of {len(task_batch)} tasks\n"
    print(prefix)
    out: Dict[str, Any] = {"log": prefix}
    results = await asyncio.gather(*[time_it(task) for task in task_batch], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log = f"{node_token} {HPARAMS['fail_token']} {task_batch[i].name} failed with {result}\n"
            print(log)
            out["log"] += log
            continue
        for name, value in result.items():
            if name == "log":
                log = f"{result['log']}\n"
                print(log)
                out["log"] += log
            else:
                out[name] = value
    suffix: str = f"{node_token} finished batch of {len(task_batch)} tasks\n"
    print(suffix)
    out["log"] += suffix
    return out


async def find_file(
    file_name: str,
    node_name: str,
    sleep: float = HPARAMS["find_file_sleep"],
    read: bool = False,
) -> Dict[str, Any]:
    filename: str = HPARAMS[f"{file_name}_filename"]
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
            out[f"{file_name}_path"] = full_path
            out[f"{file_name}_age"] = file_age
            if read:
                with open(full_path, "r") as f:
                    out[file_name] = f.read()
            break
        await asyncio.sleep(sleep)
    return out


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
    return out


async def write_log(
    log: str,
    filename: str,
    directory: str,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {"log": f"{HPARAMS['save_token']} saving logs {filename}"}
    full_path = os.path.join(directory, filename)
    with open(full_path, "a") as f:
        f.write(log)
    return out