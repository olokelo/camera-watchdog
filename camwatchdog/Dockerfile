FROM alpine:latest
COPY camwatchdog.py secrets_env.py /app/
RUN apk add --no-cache ffmpeg python3
ENTRYPOINT ["python3", "/app/camwatchdog.py"]
