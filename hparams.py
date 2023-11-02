from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class Servo:
    id: int # dynamixel id for servo
    name: str # name of servo for llm use
    range: Tuple[int, int] # (min, max) position values for servos (0, 4095)
    desc: str # description of servo for llm use

SERVOS: Dict[str, Servo] = {
    "roll" : Servo(1, "roll", (1761, 2499), "rolls the neck left and right rotating the view, roll"),
    "tilt" : Servo(2, "tilt", (979, 2223), "tilts the head up and down vertically, pitch"),
    "pan" : Servo(3, "pan", (988, 3007), "pans the head side to side horizontally, yaw")
}

@dataclass
class Pose:
    name: str # name of static pose for llm use
    angles: List[int] # list of int angles in degrees (0, 360) describing static pose
    desc: str # description of static pose for llm use

POSES: Dict[str, Pose] = {
    "home" : Pose("home", [180, 225, 180], "home/reset position, or looking up to the sky"),
    "forward" : Pose("forward", [180, 180, 180], "looking ahead, facing forward"),
    "face_left" : Pose("face_left", [180, 180, 270], "looking all the way to the left"),
    "face_right" : Pose("face_right", [180, 180, 90], "looking all the way to the right"),
    "face_down": Pose("face_down", [180, 90, 180], "looking down at the ground, facing forward")
}

@dataclass
class Move:
    name: str # name of movement for llm use
    vector: List[int] # movement vector in degrees (0, 360) one for each servo
    desc: str # description of position for llm use

MOVES: Dict[str, Move] = {
    "up" : Move("up", [0, -1, 0], "look more upwards, move slightly up"),
    "down" : Move("down", [0, 1, 0], "look more downwards, move slightly down"),
    "left" : Move("left", [0, 0, 1], "look more to the left, move slightly left"),
    "right" : Move("right", [0, 0, -1], "look more to the right, move slightly right"),
    "tilt_left" : Move("tilt_left", [-1, 0, 0], "roll or tilt head to the left"),
    "tilt_right" : Move("tilt_right", [1, 0, 0], "roll or tilt head to the right"),
}

# TODO: ALLCAPS NAMES for easy documentation and clean minimal design
# TODO: Maybe do a dataclass for an HPARAMS object?

@dataclass
class HPARAM:
    name: str
    value: any
    desc: str
    choices: Optional[List[any]] = None

HPARAMS = {
    "vlm_prompt": "Is there a person in this image? Where are they? On the left? right? center? What direction should we move the camera to get a better view of them?",
    "vlm_docker_url": "http://localhost:5000/predictions",
    "robot_llm_system_prompt": "The user will describe in natural language a desired action. Choose one of the following actions based on the command. Return only the name of the action. Here are the available actions: \n",
    "robot_llm_model": "gpt-3.5-turbo",
    "robot_llm_temperature": 0.2,
    "robot_llm_max_tokens": 32,
    "brain_data_dir": "/home/oop/dev/data/",
    "brain_ip": "192.168.1.44",
    "brain_username": "oop",
    "timeout_brain_main_loop" : 60,
    "robot_data_dir": "/home/pi/dev/data/",
    "robot_ip": "192.168.1.10",
    "robot_username": "pi",
    "timeout_robot_main_loop" : 60,
    "vizzy_data_dir": "/home/ook/dev/data/",
    "vizzy_ip": "192.168.1.10",
    "vizzy_username": "ook",
    "image_filename": "image.png",
    "image_max_age": 100000,
    "video_filename": "video.mp4",
    "robotlog_filename": "robotlog.txt",
    "brainlog_filename": "brainlog.txt",
    "commands_filename": "command.txt",
    "commands_max_age": 100000,
    "video_duration": 1,
    "video_fps": 30,
    "timeout_find_file": 2,
    "find_file_interval": 0.1,
    "timeout_send_file": 2,
    "timeout_record_video": 10,
    "timeout_take_image": 10,
    "timeout_move_servos": 2,
    "timeout_run_vlm": 2,
    "move_speed": 10,
    "move_duration": 0.8,
    "move_interval": 0.01,
    "move_servo_speed": 15, # degrees per move action
    "seed" : 42,
    "folder_stem" : "igigi",
    "date_format" : "%d.%m.%Y",
    "protocol_version" : 2.0,
    "baudrate" : 57600,
    "device_name" : "/dev/ttyUSB0",
    "addr_torque_enable" : 64,
    "addr_goal_position" : 116,
    "addr_present_position" : 132,
    "torque_enable" : 1,
    "torque_disable" : 0,
}