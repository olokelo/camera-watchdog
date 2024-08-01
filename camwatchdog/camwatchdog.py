import threading
import subprocess
import shutil
import datetime
import time
import os

from secrets_env import *

"""
Secrets should contain:

rtsp_user = ''
rtsp_password = ''
cameras = {
    'Driveway': {'stream': 'x.x.x.x/stream1'},
    'Garden': {'stream': 'x.x.x.x', 'user': '...', 'transcode_audio': False}
}
"""

output_dir = os.getenv('OUTPUT_DIR')
target_clip_length_seconds = int(os.getenv('TARGET_CLIP_LENGTH_SECONDS'))
keep_hours = int(os.getenv('KEEP_HOURS'))
assert(output_dir and target_clip_length_seconds and keep_hours)

"""
2024-06-22/
  00/
    Driveway/
    Garden/
    ...
  01/
  02/
  ...
...
"""

class Camera:

    def __init__(self, name: str, stream: str, user: str=None, password: str=None, transcode_audio: bool=True) -> None:

        self.name = name
        self.stream = stream
        self.user = user or rtsp_user  # default
        self.password = password or rtsp_password  # default
        self.transcode_audio = transcode_audio

    def build_cmd(self) -> str:

        audio_opts = '-c:a aac -b:a 32k' if self.transcode_audio else '-c:a copy'
        list_size = (keep_hours*3600) // target_clip_length_seconds

        return f'ffmpeg -loglevel warning -rtsp_transport tcp -timeout 10000000 -i "rtsp://{self.user}:{self.password}@{self.stream}" -c:v copy {audio_opts} -hls_time {target_clip_length_seconds} -hls_flags append_list+program_date_time -hls_list_size {list_size} -start_number 0 -strftime_mkdir 1 -strftime 1 -hls_start_number_source datetime -hls_segment_filename "%Y-%m-%d_%H/{self.name}/{self.name}_%Y-%m-%d_%H-%M-%S.ts" "{self.name}.m3u8"'

    def record(self) -> None:
        cmd = self.build_cmd()
        # cwd argument is very important
        subprocess.run(cmd, cwd=output_dir, shell=True)

    # record constantly even if ffmpeg crashes
    def record_loop(self) -> None:
        while True:
            try:
            	self.record()
            except:
                time.sleep(5)

# a simple thread which hourly removes clips older than keep_hours
def clip_cleaner():

    while True:

        now = datetime.datetime.now()
        seconds_to_next_hour = 3600 - (now.minute * 60 + now.second)

        # remove old clips by directory
        for item in os.listdir(output_dir):

            try:
                item_datetime = datetime.datetime.strptime(item, '%Y-%m-%d_%H')
            except ValueError:
                # ignore files/dirs that do not have this pattern in filename/dirname
                continue

            if (now-item_datetime).total_seconds() > (keep_hours+1)*3600:
                shutil.rmtree(f'{output_dir}/{item}')

        # wait until there're 10 seconds to next hour
        time.sleep(max(seconds_to_next_hour - 10, 0))

os.makedirs(output_dir, exist_ok=True)
threading.Thread(target=clip_cleaner).start()
for camname, camdata in cameras.items():
    camins = Camera(name=camname, **camdata)
    threading.Thread(target=camins.record_loop).start()
