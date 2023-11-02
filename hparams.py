from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class Servo:
    id: int  # dynamixel id for servo
    range: Tuple[int, int]  # (min, max) position values for servos (0, 4095)
    desc: str  # description of servo for llm use


@dataclass
class Pose:
    angles: List[int]  # list of int angles in degrees (0, 360) describing static pose
    desc: str  # description of static pose for llm use


@dataclass
class Move:
    vector: List[int]  # movement vector in degrees (0, 360) one for each servo
    desc: str  # description of move for llm use


@dataclass
class Camera:
    device: str  # device name for camera e.g. `/dev/video0`
    width: int  # width of camera image in pixels
    height: int  # height of camera image in pixels
    desc: str  # description of camera for llm use


@dataclass
class HPARAM:
    desc: str  # description of hparam for llm use
    value: any  # value of hparam
    choices: Optional[List[any]] = None  # TODO: Random grid search over choices


HPARAMS: Dict[str, HPARAM] = {
    "seed": HPARAM("seed", 42),
    "folder_stem": HPARAM("folder_stem", "igigi"),
    "date_format": HPARAM("date_format", "%d.%m.%Y"),
    # Brain
    "brain_data_dir": HPARAM("brain_data_dir", "/home/oop/dev/data/"),
    "brain_ip": HPARAM("brain_ip", "192.168.1.44"),
    "brain_username": HPARAM("brain_username", "oop"),
    "timeout_brain_main_loop": HPARAM("timeout_brain_main_loop", 60),
    "brainlog_filename": HPARAM("brainlog_filename", "brainlog.txt"),
    # VLM (Brain)
    "vlm_prompt": HPARAM(
        "vlm_prompt",
        "Is there a person in this image? Where are they? On the left? right? center? What direction should we move the camera to get a better view of them?",
    ),
    "vlm_docker_url": HPARAM("vlm_docker_url", "http://localhost:5000/predictions"),
    "commands_filename": HPARAM("commands_filename", "command.txt"),
    "commands_max_age": HPARAM("commands_max_age", 100000),
    "timeout_run_vlm": HPARAM("timeout_run_vlm", 2),
    # Communication
    "timeout_find_file": HPARAM("timeout_find_file", 2),
    "find_file_interval": HPARAM("find_file_interval", 0.1),
    "timeout_send_file": HPARAM("timeout_send_file", 2),
    # Robot
    "robot_data_dir": HPARAM("robot_data_dir", "/home/pi/dev/data/"),
    "robot_ip": HPARAM("robot_ip", "192.168.1.10"),
    "robot_username": HPARAM("robot_username", "pi"),
    "timeout_robot_main_loop": HPARAM("timeout_robot_main_loop", 60),
    "robotlog_filename": HPARAM("robotlog_filename", "robotlog.txt"),
    # LLM (Robot)
    "robot_llm_system_prompt": HPARAM(
        "robot_llm_system_prompt",
        "The user will describe in natural language a desired action. Choose one of the following actions based on the command. Return only the name of the action. Here are the available actions: \n",
    ),
    "robot_llm_model": HPARAM("robot_llm_model", "gpt-3.5-turbo"),
    "robot_llm_temperature": HPARAM("robot_llm_temperature", 0.2),
    "robot_llm_max_tokens": HPARAM("robot_llm_max_tokens", 32),
    # Visualization
    "vizzy_data_dir": HPARAM("vizzy_data_dir", "/home/ook/dev/data/"),
    "vizzy_ip": HPARAM("vizzy_ip", "192.168.1.10"),
    "vizzy_username": HPARAM("vizzy_username", "ook"),
    # Image
    "image_filename": HPARAM("image_filename", "image.png"),
    "image_max_age": HPARAM("image_max_age", 100000),
    "timeout_take_image": HPARAM("timeout_take_image", 10),
    # Video
    "video_filename": HPARAM("video_filename", "video.mp4"),
    "video_duration": HPARAM("video_duration", 1),
    "video_fps": HPARAM("video_fps", 30),
    "timeout_record_video": HPARAM("timeout_record_video", 10),
    # Movement parameters
    "timeout_move_servos": HPARAM("timeout_move_servos", 2),
    "move_speed": HPARAM("move_speed", 10),
    "move_duration": HPARAM("move_duration", 0.8),
    "move_interval": HPARAM("move_interval", 0.01),
    "move_servo_speed": HPARAM("move_servo_speed", 15),
    # Raw servo parameters
    "protocol_version": HPARAM("protocol_version", 2.0),
    "baudrate": HPARAM("baudrate", 57600),
    "device_name": HPARAM("device_name", "/dev/ttyUSB0"),
    "addr_torque_enable": HPARAM("addr_torque_enable", 64),
    "addr_goal_position": HPARAM("addr_goal_position", 116),
    "addr_present_position": HPARAM("addr_present_position", 132),
    "torque_enable": HPARAM("torque_enable", 1),
    "torque_disable": HPARAM("torque_disable", 0),
}

HPARAMS["poses"] = HPARAM(
    "dict of valid static poses for the servos",
    {
        "home": Pose([180, 225, 180], "home/reset position, or looking up to the sky"),
        "forward": Pose([180, 180, 180], "looking ahead, facing forward"),
        "face_left": Pose([180, 180, 270], "looking all the way to the left"),
        "face_right": Pose([180, 180, 90], "looking all the way to the right"),
        "face_down": Pose([180, 90, 180], "looking down at the ground, facing forward"),
    },
)

HPARAMS["moves"] = HPARAM(
    "dict of valid moves for the servos",
    {
        "up": Move([0, -1, 0], "look more upwards, move slightly up"),
        "down": Move([0, 1, 0], "look more downwards, move slightly down"),
        "left": Move([0, 0, 1], "look more to the left, move slightly left"),
        "right": Move([0, 0, -1], "look more to the right, move slightly right"),
        "tilt_left": Move([-1, 0, 0], "roll or tilt head to the left"),
        "tilt_right": Move([1, 0, 0], "roll or tilt head to the right"),
    },
)

HPARAMS["servos"] = HPARAM(
    "dict of servos available to robot",
    {
        "roll": Servo(
            1, (1761, 2499), "rolls the neck left and right rotating the view, roll"
        ),
        "tilt": Servo(2, (979, 2223), "tilts the head up and down vertically, pitch"),
        "pan": Servo(3, (988, 3007), "pans the head side to side horizontally, yaw"),
    },
)

HPARAMS["cameras"] = HPARAM(
    "dict of cameras available to robot",
    {
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
    },
)
