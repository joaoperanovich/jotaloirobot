FROM python:3.12-slim

# Atualiza e instala dependências de sistema
RUN apt update && apt install -y \
    ffmpeg \
    libopus0 \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev \
    gcc \
    && apt clean

# Instala dependências Python
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Inicia o bot
CMD ["python", "bot.py"]
