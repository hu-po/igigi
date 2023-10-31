HPARAMS = {
    "robot_token": "🤖",
    "servo_token": "🦾",
    "camera_token": "📷",
    # "pose_token": "🤸",
    # "move_token": "🏃",

    "vlm_prompt" : "Is there a person in this image? Where are they? On the left? right? center?",
    "vlm_docker_url" : "http://localhost:5000/predictions",

    "robot_llm_system_prompt" : "The user will describe in natural language a desired action. Choose one of the following actions based on the command. Return only the name of the action. Here are the available actions: \n",
    "robot_llm_model": "gpt-3.5-turbo",
    "robot_llm_temperature" : 0.2,
    "robot_llm_max_tokens" : 32,

    # The brain is a linux machine with a GPU that runs the VLM
    "brain_data_dir" : "/home/oop/dev/data/",
    "brain_ip" : "192.168.1.44",
    "brain_username" : "oop",

    # The robot is a raspberry pi that takes images/videos and moves servos
    "robot_data_dir" : "/home/pi/dev/data/",
    "robot_ip" : "192.168.1.10",
    "robot_username" : "pi",

    # The visualizer is a linux machine that visualizes the robot in a VR environment
    "visualizer_data_dir" : "/home/ook/dev/data/",
    "visualizer_ip" : "192.168.1.10",
    "visualizer_username" : "ook",
    
    # Communication is done by passing files around
    # logfiles are plaintext intended to be read by a LLM

    "scrape_interval" : 0.1, # seconds to wait before scraping a folder again for a file
    "scrape_timeout" : 2, # timeout in seconds for scraping a folder for a file

    # images are generally passed from robot to brain
    "image_filename" : "igigi.image.png",
    "video_filename" : "igigi.video.mp4",
    "robotlog_filename" : "igigi.robotlog.txt",
    "commands_filename" : "igigi.command.txt",

    "video_duration" : "1",
    "video_fps" : "30",
}

# # Generate a unique id for this generation session
# session_id = str(uuid.uuid4())[:6]
# hparams["session_id"] = session_id

# # Create a output folder for the session id and use that as the output dir
# hparams["brain_data_dir"] = os.path.join(hparams.get("brain_data_dir"), session_id)
# os.makedirs(hparams["brain_data_dir"], exist_ok=True)
