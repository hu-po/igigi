import os
import subprocess
import time

import gradio as gr
from hparams import HPARAMS


class ChromeUI:
    def __init__(
        self,
        output_dir: str,
        image_filename: str,
        video_filename: str,
        text_filename: str,
        display_number: str = "0.0",
        localhost_port: str = "7860",
    ):
        self.image_path = os.path.join(output_dir, image_filename)
        self.video_path = os.path.join(output_dir, video_filename)
        self.text_path = os.path.join(output_dir, text_filename)

        # Start chromium browser in kiosk mode on remote display (raspberry pi)
        os.environ["DISPLAY"] = f":{display_number}"
        _cmd = ["chromium-browser", "--kiosk", f"http://localhost:{localhost_port}"]
        self.proc = subprocess.Popen(_cmd, stdin=subprocess.PIPE)

        # self.update_interface()

    def update_interface(self):
        pass
        # with gr.Blocks() as demo:
        #     gr.Markdown("# IGIGI")
        #     with gr.Column():
        #         gr.Video(self.video_path, label="Video")
        #         gr.Image(self.image_path, label="Image")
        #         with open(self.text_path, "r") as f:
        #             text = f.read()
        #         gr.Textbox(text, label="Text")
        # demo.launch()

    def __del__(self):
        self.proc.terminate()
        os.system("killall chromium-browser")


if __name__ == "__main__":
    # Start the UI
    ui = ChromeUI(
        HPARAMS.get("robot_data_dir"),
        HPARAMS.get("video_filename"),
        HPARAMS.get("image_filename"),
        HPARAMS.get("robotlog_filename"),
    )
    for i in range(1000):
        ui.update_interface()
        time.sleep(1)
