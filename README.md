# igigi
rpi robot w/ stereo cam, 3 link head 


robot loop:

scrape for servo commands
scrape for image commands

take image, write image log, send image + image log
move servos, write servo log, send servo log

brain loop:

scrape for user commands
scrape for image + image log
scrape for servo + servo log

ask llm for servo commands, write servo commands, send servo commands
ask llm for image commands, write image commands, send image commands