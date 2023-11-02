import os
import uuid
import random
from pprint import pprint

from datetime import datetime

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

HPARAMS: Dict[str, Any] = {
    "brain_token": "🧠",
    "robot_token": "🤖",
    "viewr_token": "🖼️",
    "image_token": "📷",
    "video_token": "📹",
    "find_token" : "🔍",
    "fail_token" : "❌",
    "send_token" : "📤",
    "time_token": "⏱️",
    "user_token": "👤",
    "servos_token": "🦾",
    "move_token": "🦿",
    "save_token": "💾",
    "up_token": "🔝",
    "down_token": "⤵️",
    "left_token": "🔙",
    "right_token": "🔜",
    # "scan_token": "🔛",
    # "_token": "⤴️",
}

@dataclass
class Servo:
    id: int  # dynamixel id for servo
    range: Tuple[int, int]  # (min, max) position values for servos (0, 4095)
    desc: str  # description of servo for llm use


HPARAMS["servos"] = {
    "roll": Servo(1, (1761, 2499), "rolls the neck left and right, roll"),
    "tilt": Servo(2, (979, 2223), "tilts the head up and down vertically, pitch"),
    "pan": Servo(3, (988, 3007), "pans the head side to side horizontally, yaw"),
}


@dataclass
class Pose:
    angles: List[int]  # list of int angles in degrees (0, 360) describing static pose
    desc: str  # description of static pose for llm use


HPARAMS["poses"] = {
    # "home": Pose([180, 225, 180], "home/reset position, or looking up to the sky"),
    "forward": Pose(
        [180, 180, 180],
        "looking ahead, facing forward, default option if you are uncertain",
    ),
    # "face_left": Pose([180, 180, 270], "looking all the way to the left"),
    # "face_right": Pose([180, 180, 90], "looking all the way to the right"),
    # "face_down": Pose([180, 90, 180], "looking down at the ground, facing forward"),
}


@dataclass
class Move:
    vector: List[int]  # movement vector in degrees (0, 360) one for each servo
    desc: str  # description of move for llm use


HPARAMS["moves"] = {
    HPARAMS["up_token"] : Move([0, 1, 0], "look up, move slightly upwards"),
    HPARAMS["left_token"] : Move([0, 0, 1], "look left, move slightly leftwards"),
    HPARAMS["down_token"] : Move([0, -1, 0], "look down, move slightly downwards"),
    HPARAMS["right_token"] : Move([0, 0, -1], "look right, move slightly rightwards"),
    #     "tilt_left": Move([-1, 0, 0], "roll or tilt head to the left"),
    #     "tilt_right": Move([1, 0, 0], "roll or tilt head to the right"),
}


@dataclass
class Camera:
    device: str  # device name for camera e.g. `/dev/video0`
    width: int  # width of camera image in pixels
    height: int  # height of camera image in pixels
    desc: str  # description of camera for llm use


HPARAMS["cameras"] = {
    "stereo": Camera(
        device="/dev/video0",
        width=1280,
        height=480,
        desc="front facing stereo camera",
    ),
    "mono": Camera(
        device="/dev/video2",
        width=640,
        height=480,
        desc="front facing monocular camera, forehead",
    ),
}

# Brain is the main computer that runs the VLM on a GPU
HPARAMS["brain_ip"]: str = "192.168.1.44"
HPARAMS["brain_username"]: str = "oop"
HPARAMS["brain_data_dir"]: str = "/home/oop/dev/data/"
HPARAMS["brainlog_filename"]: str = f"log.{HPARAMS['brain_token']}.txt"
HPARAMS["brainlog_max_age"]: int = 120 # seconds
HPARAMS["vlm_prompt"]: str = "Stereo left and right. Can I see the person? How should I move my head to find the person? Stereo POV camera."
HPARAMS["vlm_docker_url"]: str = "http://localhost:5000/predictions"
HPARAMS["vlmout_filename"]: str = "vlmout.txt"

# Robot is the Raspberry Pi that controls the Servos, Cameras
HPARAMS["robot_ip"]: str = "192.168.1.10"
HPARAMS["robot_username"]: str = "pi"
HPARAMS["robot_data_dir"]: str = "/home/pi/dev/data/"
HPARAMS["robotlog_filename"]: str = f"log.{HPARAMS['robot_token']}.txt"
HPARAMS["robotlog_max_age"]: int = 120 # seconds
HPARAMS["robot_llm_prompt"]: str = "Choose the best action based on the user description. Return only the name. Here are the available actions: \n"
HPARAMS["robot_llm_model"]: str = "gpt-3.5-turbo"
HPARAMS["robot_llm_temperature"]: float = 0.2
HPARAMS["robot_llm_max_tokens"]: int = 24
# Image
HPARAMS["image_filename"]: str = "image.png"
HPARAMS["image_max_age"]: int = 100000
# Video
HPARAMS["video_filename"]: str = "video.mp4"
HPARAMS["video_duration"]: int = 1 # seconds
HPARAMS["video_fps"]: int = 30 # frames per second
# Movement parameters
HPARAMS["default_pose"]: str = "forward"
HPARAMS["set_servo_speed"]: int = 32 # degrees per move duration
HPARAMS["set_servo_duration"]: float = 1.6 # seconds
HPARAMS["set_servo_sleep"]: float = 0.001 # seconds
# Raw servo parameters
HPARAMS["protocol_version"]: float = 2.0
HPARAMS["baudrate"]: int = 57600
HPARAMS["device_name"]: str = "/dev/ttyUSB0"
HPARAMS["addr_torque_enable"]: int = 64
HPARAMS["addr_goal_position"]: int = 116
HPARAMS["addr_present_position"]: int = 132
HPARAMS["torque_enable"]: int = 1
HPARAMS["torque_disable"]: int = 0

# Viewer is a secondary computer that runs a VR WebXR visualization tool
HPARAMS["viewr_ip"]: str = "192.168.1.10"
HPARAMS["viewr_username"]: str = "ook"
HPARAMS["viewr_data_dir"]: str = "/home/ook/dev/data/"

# Misc
HPARAMS["find_file_sleep"]: float = 0.1
HPARAMS['time_format']: str = "%H:%M:%S"

# Misc
HPARAMS["seed"]: int = 42
HPARAMS["folder_stem"]: str = "igigi"
HPARAMS["date_format"]: str = "%d.%m.%Y"

# Create unique session folder based on seed and date
random.seed(HPARAMS["seed"])
session_id = str(uuid.UUID(int=random.getrandbits(128)))[:6]
current_date = datetime.now().strftime(HPARAMS["date_format"])
HPARAMS["session_name"] = f"{HPARAMS['folder_stem']}.{session_id}.{current_date}"

# Modify data directories
HPARAMS["brain_data_dir"] = os.path.join(
    HPARAMS["brain_data_dir"], HPARAMS["session_name"]
)
HPARAMS["robot_data_dir"] = os.path.join(
    HPARAMS["robot_data_dir"], HPARAMS["session_name"]
)
HPARAMS["viewr_data_dir"] = os.path.join(
    HPARAMS["viewr_data_dir"], HPARAMS["session_name"]
)

pprint(HPARAMS)
