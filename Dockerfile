# 🌱 Base: Python 3.12 com ffmpeg
FROM python:3.12-slim

# 🧰 Instala ffmpeg e dependências do yt_dlp
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 🔧 Cria diretório de trabalho
WORKDIR /app

# 📦 Copia todos os arquivos para o container
COPY . .

# 📦 Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# ▶️ Comando de inicialização
CMD ["python", "bot.py"]
