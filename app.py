import os
import subprocess
import sys
import logging
import time

import gradio as gr
from hparams import HPARAMS

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def remote_chromium_gradio_ui(
    display_number: str = "0.0",
    localhost_port: str = "7860",
):
    # Start chromium browser in kiosk mode on remote display (raspberry pi)
    os.environ["DISPLAY"] = f":{display_number}"
    _cmd = ["chromium-browser", "--kiosk", f"http://localhost:{localhost_port}"]
    return subprocess.Popen(_cmd, stdin=subprocess.PIPE)


def display_video_image_text(video_path, image_path, text_path):
    """Displays a video, image, and text file from local paths."""

    # Load the video, image, and text file.
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    with open(text_path, "r") as f:
        text = f.read()

    # Create the Gradio Interface.
    interface = gr.Interface(fn=display_video_image_text, inputs=[], outputs=["video", "image", "text"])

    # Set the initial values of the output components.
    interface.outputs["video"].update(video_bytes)
    interface.outputs["image"].update(image_bytes)
    interface.outputs["text"].update(text)

    # Start a loop to refresh the output components every 1 second.
    while True:
        interface.refresh()
        time.sleep(1)

if __name__ == "__main__":
    try:
        process = remote_chromium_gradio_ui()
        display_video_image_text(
            os.path.join(HPARAMS.get("robot_data_dir"), HPARAMS.get("video_filename")),
            os.path.join(HPARAMS.get("robot_data_dir"), HPARAMS.get("image_filename")),
            os.path.join(HPARAMS.get("robot_data_dir"), HPARAMS.get("robotlog_filename")),
        )
    except KeyboardInterrupt:
        print("Remote chromium browser terminated.")
        sys.exit(0)
    except subprocess.CalledProcessError:
        print("Error: chromium process failed.")
