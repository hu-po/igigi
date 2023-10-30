import os
import asyncio

async def scrape_callback(
    directory: str, 
    filename: str, 
    callback: callable,
    interval: int = 1, 
    timeout: int = 60,
):
    try:
        async def _scrape():
            while True:
                if filename in os.listdir(directory):
                    full_path = os.path.join(directory, filename)
                    if asyncio.iscoroutinefunction(callback):
                        await callback(full_path)
                    else:
                        callback(full_path)
                await asyncio.sleep(interval)
        
        await asyncio.wait_for(_scrape(), timeout=timeout)
    except asyncio.TimeoutError:
        print("Timeout reached. Stopping the function.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def send_file(
    filename: str,
    local_dir_path: str,
    remote_dir_path: str,
    remote_username: str,
    remote_ip: str,
) -> None:
    local_path = os.path.join(local_dir_path, filename)
    remote_path = os.path.join(remote_dir_path, filename)
    cmd = ["scp", local_path, f"{remote_username}@{remote_ip}:{remote_path}"]
    print(f"Running command: {cmd}")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    print(f"Sent {local_path} to {remote_path}\n")

async def llm_func(
    llm_func: callable,
    system_msg: str,
    prompt_msg: str,
    max_tokens: int,
) -> str:
    msg: str = ""
    desired_pose_name = llm_func(
            max_tokens=8,
            messages=[
                {"role": "system", "content": f"{system_msg}\n{move_msg}"},
                {"role": "user", "content": raw_move_str},
            ]
    )
    msg += f"{MOVE_TOKEN} commanded pose is {desired_pose_name}\n"
    desired_pose = POSES.get(desired_pose_name, None)
    if desired_pose is not None:
        return robot.move(desired_pose.angles)
    else:
        msg += f"ERROR: {desired_pose_name} is not a valid pose.\n"
        return msg


# Example usage with an asynchronous callback:
# async def async_print_path(path):
#     await asyncio.sleep(1)  # Just simulating some async operation here.
#     print(f"File found at: {path}")
# asyncio.run(scrape_callback('.', 'myfile.txt', async_print_path))
