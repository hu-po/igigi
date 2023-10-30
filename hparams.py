HPARAMS = {
    # The brain is a linux machine with a GPU that runs the VLM
    "brain_data_dir" : "/home/oop/dev/data/",
    "brain_ip" : "192.168.1.44",
    "brain_username" : "oop",
    # The robot is a raspberry pi that takes images/videos and moves servos
    "robot_data_dir" : "/home/pi/dev/data/",
    "robot_ip" : "192.168.1.10",
    "robot_username" : "pi",
    
    # Communication is done by passing files around
    # logfiles are plaintext intended to be read by a LLM

    # images are generally passed from robot to brain
    "robot_image_filename" : "igigi.image.png",
    "robot_imagelog_filename" : "igigi.image.txt",

    # videos are generally passed from robot to brain
    "robot_video_filename" : "igigi.video.mp4",
    "robot_videolog_filename" : "igigi.video.txt",
    "duration" : "1",
    "fps" : "30",

    # commands are generally passed from brain to robot
    "commands_filename" : "igigi.command.txt",
    "commandslog_filename" : "igigi.command.txt",
 
}