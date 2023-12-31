# igigi

Multi-computer, multi-modal robot that uses AI to interact with the world.

### Description

The three main nodes are:

`robot` - A Raspbery Pi with a 3-link arm, a monocular camera, and a stereo camera.
`brain` - A linux server with a GPU that runs a VLM
`vizzi` - A linux server that runs a VR visualizer for the robot

### VLM (Video Language Model)

LLaVA 13B running locally at 8bit on a docker container (14G VRAM)

```
# Download original model from HuggingFace https://huggingface.co/liuhaotian/llava-v1.5-13b/tree/main
# Use replicate docker container: https://replicate.com/yorickvp/llava-13b
docker run --name llava13b r8.im/yorickvp/llava-13b@sha256:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591
docker commit llava13b llava13b

# Use mounted volume for locally stored weights (will also download clip336)
docker run -v /home/oop/dev/LLaVA/llava-v1.5-13b:/src/liuhaotian/llava-v1.5-13b --gpus=all llava13b
docker commit FOOO llava13b

# Inside src/predict.py you have to change line 85 "load_8bit=True"
docker run -it -v /home/oop/dev/LLaVA/llava-v1.5-13b:/src/liuhaotian/llava-v1.5-13b --gpus=all llava13b
docker cp 68f397c04dc0:/src/predict.py predict.py
docker cp predict.py 68f397c04dc0:/src/predict.py
docker commit 68f397c04dc0 llava13b
```

### LLM (Language Language Model)

GPT-4 via API (OpenAI)

### Visualization

VR visualization is done via WebXR and a Quest Pro

### Viewing Cameras

```
ssh -L 12345:localhost:12345 pi@192.168.1.10
ffmpeg -f v4l2 -framerate 30 -video_size 1280x480 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -f mpegts tcp://0.0.0.0:12345?listen
ffmpeg -f v4l2 -framerate 30 -video_size 320x240 -i /dev/video2 -c:v libx264 -preset ultrafast -tune zerolatency -f mpegts tcp://0.0.0.0:12345?listen

ffplay tcp://localhost:12345
```

### Notes

All nodes must be communicating via local network, set up ssh keys for passwordless login.