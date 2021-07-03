import json
import os
import random
import re
import sys
import tempfile
import uuid
from shutil import rmtree

import ffmpeg
import pyperclip
import requests
import yaml
from pynotifier import Notification
from tqdm import tqdm

SM_ROOT = 'https://sm.ms/api/v2/'
SM_TOKEN = 'Expected to be updated from config.yaml'
CONFIG_FILE = os.path.join(os.path.split(__file__)[0], 'config.yaml')

IMG_URL_EXTRACT = r'(https?://\S+)'
TMP_DIR = os.path.join(tempfile.gettempdir(), f"{uuid.uuid1()}")
os.makedirs(TMP_DIR)


def read_yaml_config(config_file=CONFIG_FILE):
    global SM_TOKEN
    try:
        assert os.path.exists(config_file), "[Error] no config file!"
        with open(config_file, "r", encoding="utf-8") as yaml_file:
            config = yaml.safe_load(yaml_file)
            SM_TOKEN = config['sm_token']
            return config
    except Exception as e:
        exit_with_error(str(e))


def exit_with_error(error_msg):
    Notification(
        title='Script failed with error!',
        description=f'{error_msg}',
        duration=3,
        urgency='critical'
    ).send()
    rmtree(TMP_DIR, ignore_errors=True)
    sys.exit(1)


def get_time_frames_for_screen_shot(video_duration, num_screen_shots):
    start = int(video_duration*0.2)
    end = int(video_duration*0.8)
    return [random.randrange(start, end) for i in range(num_screen_shots)]


def get_video_duration(video_path):
    try:
        info = ffmpeg.probe(video_path)
        return float(info['format']['duration'])
    except ffmpeg.Error as e:
        exit_with_error(e.stderr.decode())


def get_screen_shots(video_path, time_frames):
    img_paths = []
    print("Taking screenshots")
    for index, frame in tqdm(enumerate(time_frames), total=len(time_frames)):
        cur_path = os.path.join(TMP_DIR, f"temp_screenshot_{index}.jpg")
        create_screen_shot(video_path, frame, cur_path)
        assert os.path.exists(cur_path), "Screenshot failed"
        img_paths.append(cur_path)
    return img_paths


def create_screen_shot(video_path, frame, save_path):
    try:
        (
            ffmpeg
            .input(video_path, ss=frame)
            .output(save_path, vframes=1, **{'qscale:v': 5})
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)


# Adapted from: https://github.com/XavierJiezou/python-sm.ms-api/blob/master/smms.py
def upload_image(imgpath):
    try:
        files = {'smfile': open(imgpath, 'rb')}
        headers = {'Authorization': SM_TOKEN}
        url = SM_ROOT+'upload'
        res = requests.post(url, files=files, headers=headers, proxies={}).json()
        if res['success']:
            img_url = res['data']['url']
            return img_url
        else:
            res_msg = res['message']
            extracted_url = re.match(IMG_URL_EXTRACT, res_msg)
            if extracted_url and extracted_url.endswith(".jpg"):
                return extracted_url
            print(res['message'])
            exit_with_error("Unable to upload image to host")
    except Exception as e:
        print(e)
        exit_with_error("Unable to upload image to host")


def create_bbcode_from_url(url_path):
    return f"[img]{url_path}[/img]"


if __name__ == "__main__":
    print(__file__)
    config = read_yaml_config()
    if len(sys.argv) != 2:
        print("Expected to have a video file as input")
        exit_with_error("Expected to have a video file as input")
    droppedFile = sys.argv[1]
    video_path = droppedFile
    duration = get_video_duration(video_path)
    time_frames = get_time_frames_for_screen_shot(duration, 3)
    print(f"duration: {duration}")
    print(f"time_frames: {time_frames}")
    print(f"TMP_PATH: {TMP_DIR}")
    screenshot_paths = get_screen_shots(video_path, time_frames)
    print(screenshot_paths)
    print("Uploading to sm.ms")
    img_urls = [upload_image(i) for i in tqdm(screenshot_paths)]
    img_urls = [create_bbcode_from_url(i) for i in img_urls]
    pyperclip.copy("\n".join(img_urls))
    print("Success! BBCode copied to clipboard")
    Notification(
        title='BBCode copied to clipboard',
        description="\n".join(img_urls),
        duration=3,
        urgency='normal'
    ).send()

rmtree(TMP_DIR, ignore_errors=True)
