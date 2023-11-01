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
    "robot_data_dir": "/home/pi/dev/data/",
    "robot_ip": "192.168.1.10",
    "robot_username": "pi",
    "vizzy_data_dir": "/home/ook/dev/data/",
    "vizzy_ip": "192.168.1.10",
    "vizzy_username": "ook",
    "image_filename": "igigi.image.png",
    "video_filename": "igigi.video.mp4",
    "robotlog_filename": "igigi.robotlog.txt",
    "commands_filename": "igigi.command.txt",
    "video_duration": 1,
    "video_fps": 30,
    "timeout_find_file": 2,
    "timeout_send_file": 2,
    "timeout_record_video": 2,
    "timeout_take_image": 2,
    "timeout_move_servos": 2,
    "timeout_run_vlm": 2,
    "move_epsilon_degrees": 10,
    "move_timeout_seconds": 0.8,
    "move_interval_seconds": 0.01,
}

# TODO: Make unique folders for each run, somehow use same uuid for all computers

# # Generate a unique id for this generation session
# session_id = str(uuid.uuid4())[:6]
# hparams["session_id"] = session_id

# # Create a output folder for the session id and use that as the output dir
# hparams["brain_data_dir"] = os.path.join(hparams.get("brain_data_dir"), session_id)
# os.makedirs(hparams["brain_data_dir"], exist_ok=True)
