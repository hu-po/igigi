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
    "move_epsilon_degrees": 10,
    "move_timeout_seconds": 0.8,
    "move_interval_seconds": 0.01,
    "move_servo_speed": 5, # degrees per move action
    "seed" : 42,
    "folder_stem" : "igigi",
    "date_format" : "%d.%m.%Y",
}