import discord
import os
import requests
import datetime
import asyncio
import yt_dlp

from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GNEWS_API_KEY = "c5c3ead197b2b007803b75113a119ec1"
GOOGLE_SEARCH_API_KEY = "AIzaSyBD7SREyLvYv5dB4vbuGYnqMMSVnFjRegc"
GOOGLE_SEARCH_ENGINE_ID = "6086735b529b34411"

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
client_openai = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!jota ', intents=intents)

# Funções auxiliares
def buscar_no_google(prompt):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={prompt}&key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}"
        r = requests.get(url)
        data = r.json()
        if "items" not in data:
            return "❌ Nenhum resultado relevante foi encontrado."
        resposta = f"🔎 Resultados do Google para: **{prompt}**\n\n"
        for item in data["items"][:3]:
            resposta += f"• {item.get('title')}\n{item.get('snippet')}\n{item.get('link')}\n\n"
        return resposta.strip()
    except Exception as e:
        return f"❌ Erro ao buscar no Google: {e}"

def buscar_na_web(prompt):
    prompt_lower = prompt.lower()
    if any(x in prompt_lower for x in ["dólar", "cotação", "real", "euro", "quanto custa", "valor do", "preço"]):
        try:
            r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=BRL")
            valor = r.json()["rates"]["BRL"]
            return f"O dólar hoje está cotado a R$ {valor:.2f}."
        except:
            return "Erro ao obter cotação."
    elif any(x in prompt_lower for x in ["notícia", "hoje", "últimas", "aconteceu"]):
        try:
            r = requests.get(f"https://gnews.io/api/v4/search?q={prompt}&lang=pt&max=3&apikey={GNEWS_API_KEY}")
            noticias = r.json()["articles"]
            resposta = f"🗞️ Resultados de busca por: **{prompt}**\n\n"
            for n in noticias:
                data_pub = datetime.datetime.fromisoformat(n["publishedAt"].replace("Z", "+00:00"))
                resposta += f"• {n['title']} ({data_pub.strftime('%d/%m %H:%M')})\n{n['url']}\n\n"
            return resposta.strip()
        except:
            return "Erro ao buscar notícias."
    else:
        return buscar_no_google(prompt)

# Inicialização
@bot.event
async def on_ready():
    print(f'🤖 Bot está online como {bot.user}')

# Controle da fila de músicas
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

def push_queue(guild_id, title, url):
    if guild_id not in queues:
        queues[guild_id] = []
    queues[guild_id].append({'title': title, 'stream': url})




async def verifica_inatividade(vc, ctx, timeout=60):
    await asyncio.sleep(timeout)
    if not vc.is_playing() and not get_queue(ctx.guild.id):
        await ctx.send("💤 Sem música por um tempo. Saindo do canal de voz.")
        await vc.disconnect()

# Mensagens
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!limpar'):
        await message.channel.send("🧹 Limpando mensagens do canal...")
        try:
            await message.channel.purge(check=lambda m: m.author == message.author or m.author == bot.user)
        except Exception as e:
            await message.channel.send(f"❌ Erro ao apagar mensagens: {e}")
        return

    if message.content.startswith('!jota'):
        prompt = message.content[len('!jota'):].strip()

        cmd = prompt.split(" ")[0].lower()
        if cmd in ["play", "stop", "next", "resume", "fila", "clear", "ajuda"]:

            await bot.process_commands(message)
            return

        if prompt.lower().startswith("p "):
            termo = prompt[2:].strip()
            await message.channel.send("🌐 Pesquisando diretamente no Google...")
            try:
                conteudo = buscar_na_web(termo)
                resposta = gemini_model.generate_content(
                    f"""Com base nas informações coletadas abaixo, responda à pergunta do usuário de forma natural:

🔎 Pergunta: {termo}
📄 Resultados:
{conteudo}

Não diga que você não tem acesso à internet. Responda naturalmente."""
                )
                texto = resposta.text if resposta and resposta.text else "⚠️ Nenhuma resposta gerada."
                await message.channel.send(texto)
            except Exception as e:
                await message.channel.send(f"❌ Erro: {e}")
            return

        await message.channel.send("💬 Processando com GPT-3.5...")
        try:
            chat_completion = client_openai.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "Você é um assistente útil que responde no Discord."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            reply = chat_completion.choices[0].message.content
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"❌ Erro com GPT: {e}")
        return



# 🎵 Comando !jota play
@bot.command(name='play')
async def play(ctx, *, search: str):
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        return await ctx.send("❌ Você precisa estar em um canal de voz para tocar música.")

    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc:
        try:
            vc = await voice_channel.connect()
        except Exception as e:
            return await ctx.send(f"❌ Erro ao entrar no canal de voz: {e}")

    await ctx.send(f"🔍 Procurando: **{search}**...")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
        'forcejson': True,
        #'simulate': True,
        'source_address': '0.0.0.0',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    }

    try:
        search_term = search
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_term, download=False)
        if 'entries' in info:
            info = ydl.extract_info(info['entries'][0]['webpage_url'], download=False)
            title = info.get('title', 'Música')
            formats = info.get('formats', [])
            
            # Tenta extrair um stream de áudio válido
            stream_url = None
            for f in formats:
                if (
                    f.get('acodec') not in [None, 'none'] and
                    f.get('vcodec') in [None, 'none'] and
                    f.get('url') and
                    f.get('ext') in ['m4a', 'webm']
                ):
                    stream_url = f['url']
                    break

            
            print(f"[DEBUG] Música encontrada: {title}")
            print(f"[DEBUG] URL usada: {stream_url}")
            

    except Exception as e:
        await ctx.send(f"❌ Erro ao buscar a música: {e}")
        return

    # ✅ ADICIONA AQUI
    push_queue(ctx.guild.id, title, stream_url)

    if not vc.is_playing():
        play_next(ctx, vc, ctx.guild.id)
    else:
        await ctx.send(f"✅ **{title}** adicionada à fila.")



# ▶️ Função para tocar a próxima música da fila (streaming)
def play_next(ctx, vc, guild_id):
    queue = get_queue(guild_id)

    if queue:
        next_song = queue.pop(0)
        title = next_song['title']
        stream_url = next_song['stream']

        def after_play(error):
            if error:
                print(f"[ERRO] Falha ao tocar: {error}")
            else:
                print(f"[INFO] Música finalizada: {title}")
            play_next(ctx, vc, guild_id)

        try:
            print(f"[DEBUG] Tocando: {title}")
            print(f"[DEBUG] URL: {stream_url}")
            vc.play(
                discord.FFmpegPCMAudio(
                    stream_url,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                ),
                after=after_play
            )
            asyncio.run_coroutine_threadsafe(ctx.send(f"▶️ Tocando agora: **{title}**"), bot.loop)
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar reprodução: {e}")
            asyncio.run_coroutine_threadsafe(ctx.send(f"❌ Erro ao iniciar reprodução: {e}"), bot.loop)
    else:
        asyncio.run_coroutine_threadsafe(verifica_inatividade(vc, ctx, 60), bot.loop)


# ⏸️ Pausar música
@bot.command(name='stop')
async def stop(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Música pausada.")
    else:
        await ctx.send("❌ Não estou tocando nada agora.")

# ▶️ Retomar música
@bot.command(name='resume')
async def resume(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Música retomada.")
    else:
        await ctx.send("❌ Não tem música pausada pra retomar.")

# ⏭️ Pular para a próxima
@bot.command(name='next')
async def next(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ Pulando para a próxima música...")
    else:
        await ctx.send("❌ Não estou tocando nada no momento.")

# 📋 Ver fila
@bot.command(name='fila')
async def fila(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("📭 A fila está vazia.")
    else:
        lista = "\n".join([f"{i+1}. {m['title']}" for i, m in enumerate(queue)])
        await ctx.send(f"📃 Fila de músicas:\n{lista}")

# 🗑️ Limpar fila
@bot.command(name='clear')
async def clear(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    queue = get_queue(ctx.guild.id)
    queue.clear()
    if vc and vc.is_playing():
        vc.stop()
    await ctx.send("🗑️ Fila limpa e música parada.")

@bot.command(name='ajuda')
async def ajuda(ctx):
    comandos = """
🎯 **Agora você pode usar:**

🎵 **Comandos de música**
• `!jota play [nome ou link]` → adiciona à fila e toca
• `!jota stop` → pausa a música
• `!jota resume` → volta a tocar
• `!jota next` → pula pra próxima música
• `!jota fila` → mostra o que está na fila
• `!jota clear` → limpa a fila e para a música

🧠 **Comandos de IA e busca**
• `!jota p [pergunta]` → busca no Google e responde com Gemini
• `!jota [pergunta]` → responde direto com GPT-3.5

🧹 **Outros comandos**
• `!limpar` → apaga suas mensagens no canal atual

"""
    await ctx.send(comandos)

# Inicia o bot
bot.run(DISCORD_TOKEN)
