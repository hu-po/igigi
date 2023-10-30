import os
import asyncio
from datetime import timedelta

ROBOT_DATA_DIR = "/home/pi/dev/data/"
REMOTE_DATA_DIR = "/home/oop/dev/data/"
REMOTE_USERNAME = "oop"
REMOTE_IP = "192.168.1.44"

async def scrape_callback(
    directory: str, 
    filename: str, 
    callback: callable, 
    interval: timedelta = timedelta(seconds=3), 
    timeout: timedelta = timedelta(minutes=1)
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
                await asyncio.sleep(interval.total_seconds())
        
        await asyncio.wait_for(_scrape(), timeout=timeout.total_seconds())
    except asyncio.TimeoutError:
        print("Timeout reached. Stopping the function.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def send_file(
    filename: str,
    robot_dir_path: str = ROBOT_DATA_DIR,
    remote_dir_path: str = REMOTE_DATA_DIR,
    username: str = REMOTE_USERNAME,
    remote_ip: str = REMOTE_IP,
) -> str:
    msg: str = ""
    local_path = os.path.join(robot_dir_path, filename)
    remote_path = os.path.join(remote_dir_path, filename)
    cmd = ["scp", local_path, f"{username}@{remote_ip}:{remote_path}"]
    print(f"Running command: {cmd}")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    msg += f"Sent {local_path} to {remote_path}\n"
    if process.returncode != 0:
        msg += f"ERROR on send: {stderr.decode()}"
    return msg


# Example usage with an asynchronous callback:
# async def async_print_path(path):
#     await asyncio.sleep(1)  # Just simulating some async operation here.
#     print(f"File found at: {path}")
# asyncio.run(scrape_callback('.', 'myfile.txt', async_print_path))
