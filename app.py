import os
import subprocess

import gradio as gr
from hparams import HPARAMS


class ChromeUI:
    def __init__(
        self,
        display_number: str = "0.0",
        localhost_port: str = "7860",
    ):
        self.nuke()
        self.wake()
        # Wake up screen (raspberry pi)
        # Start chromium browser in kiosk mode on remote display (raspberry pi)
        os.environ["DISPLAY"] = f":{display_number}"
        _cmd = ["chromium-browser", "--kiosk", f"http://localhost:{localhost_port}"]
        self.proc = subprocess.Popen(_cmd, stdin=subprocess.PIPE)
    
    def nuke(self):
        os.system("killall chromium-browser")

    def wake(self):
        os.system('xdotool key shift')

    def __del__(self):
        self.proc.terminate()
        self.nuke()

with gr.Blocks() as demo:
    gr.Markdown("# IGIGI")
    with gr.Column():
        _path = os.path.join(HPARAMS["robot_data_dir"], "image.png") # HPARAMS["image_filename"])
        img = gr.Image(_path, every=1, show_download_button=False, show_label=False)
        # _path = os.path.join(HPARAMS["robot_data_dir"], HPARAMS["robotlog_filename"])
        # with open(_path, "r") as f:
        #     text = f.read()
        # gr.Textbox(text, label="Text")


if __name__ == "__main__":
    ui = ChromeUI()
    demo.queue().launch()

