FROM python:3.12-slim

RUN apt update && apt install -y ffmpeg

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
# Dockerfile for JOTALOIROCITY Discord Bot
# This Dockerfile sets up a Python environment with FFmpeg for audio processing.