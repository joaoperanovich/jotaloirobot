# 🤖 JotaloiroBot

O **JotaloiroBot** é um bot de Discord completo com:
- 🎧 Reprodução de música com fila
- 🧠 Integração com ChatGPT (OpenAI) e Gemini (Google)
- 🌎 Respostas com busca real no Google
- 🎛️ Comandos interativos e prontos para uso

---

## 📜 Comandos disponíveis

### 🎵 Música
| Comando                  | Função                                 |
|--------------------------|----------------------------------------|
| `!jota play [nome/link]` | Toca música ou adiciona à fila         |
| `!jota stop`             | Pausa a música atual                   |
| `!jota resume`           | Retoma a música pausada                |
| `!jota next`             | Pula para a próxima da fila            |
| `!jota fila`             | Mostra as músicas na fila              |
| `!jota clear`            | Limpa a fila e para a reprodução       |

### 🧠 Inteligência Artificial
| Comando                 | Função                                             |
|-------------------------|----------------------------------------------------|
| `!jota [pergunta]`      | Responde usando o GPT-3.5 da OpenAI                |
| `!jota p [pergunta]`    | Faz busca no Google e responde com Gemini (Google)|

### 🧹 Utilitários
| Comando     | Função                                  |
|-------------|-----------------------------------------|
| `!limpar`   | Apaga suas mensagens do canal atual     |
| `!jota ajuda` | Lista todos os comandos disponíveis    |

---

## 🚀 Tecnologias usadas

- Python 3.10+
- [discord.py](https://discordpy.readthedocs.io)
- [yt_dlp](https://github.com/yt-dlp/yt-dlp)
- [OpenAI](https://platform.openai.com/)
- [Google Generative AI](https://ai.google.dev/)
- Railway (deploy automático)

---

## 📦 Instalação local

```bash
git clone https://github.com/joaoperanovich/jotaloirobot.git
cd jotaloirobot
pip install -r requirements.txt
