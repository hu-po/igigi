import os
import asyncio


async def scrape(
    filename: str,
    directory: str,
    interval: float,
    timeout: int,
):
    print(f"Scraping {filename} from {directory} every {interval} seconds.")
    try:

        async def _scrape():
            while True:
                if filename in os.listdir(directory):
                    full_path = os.path.join(directory, filename)
                    return full_path
                await asyncio.sleep(interval)

        return await asyncio.wait_for(_scrape(), timeout=timeout)
    except asyncio.TimeoutError:
        print("Timeout reached. Stopping the function.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


async def send_file(
    filename: str,
    local_dir_path: str,
    remote_dir_path: str,
    remote_username: str,
    remote_ip: str,
) -> None:
    local_path = os.path.join(local_dir_path, filename)
    remote_path = os.path.join(remote_dir_path, filename)
    print(f"Sending {local_path} to {remote_path}\n")
    cmd = ["scp", local_path, f"{remote_username}@{remote_ip}:{remote_path}"]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()


async def write_log(
    log: str,
    filename: str,
    output_dir: str,
):
    output_path: str = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        f.write(log)