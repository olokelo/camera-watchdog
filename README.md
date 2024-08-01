# Camera Watchdog

A simple Python script and Docker Compose stack for recording videos from RTSP cameras. Personally I use it as a backup if Frigate were ever to crash.

# How to use

Generate HTTP Basic Auth user and password used for web interface
```shell
$ pip install bcrypt
$ python gen_htpasswd.py
```

Create `camwatchdog/secrets_env.py`
```python
rtsp_user = ''
rtsp_password = ''
cameras = {
    'Driveway': {'stream': 'x.x.x.x/stream1'},
    'Garden': {'stream': 'x.x.x.x', 'user': '...', 'transcode_audio': False}
}
```

Create `.env` file with the following contents and adjust parameters to your needs
```shell
HOST_OUTPUT_DIR=/mnt/datadir
TARGET_CLIP_LENGTH_SECONDS=10
KEEP_HOURS=24
WEB_PORT=8080
```
- `HOST_OUTPUT_DIR` - output directory for recordings and m3u8 files
- `TARGET_CLIP_LENGTH_SECONDS` - how long should each HLS segment be
- `KEEP_HOURS` - clips older than that will be automatically removed every hour
- `WEB_PORT` - port of web interface

Start the stack
```shell
$ docker compose up -d
```

# Other

This repository contains minified [hls.js](https://github.com/video-dev/hls.js) library licensed under Apache 2.0.
