import subprocess
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotReloadHandler(FileSystemEventHandler):
    def __init__(self, filepath):
        self.filepath = filepath
        self.process = None
        self.run_bot()

    def run_bot(self):
        if self.process:
            self.process.terminate()
            print("🔁 Bot reiniciado")
        self.process = subprocess.Popen(["python", self.filepath])

    def on_modified(self, event):
        if event.src_path.endswith(self.filepath):
            print("💾 Detecção de modificação. Reiniciando bot...")
            self.run_bot()

if __name__ == "__main__":
    path_to_watch = "."
    bot_file = "bot.py"

    event_handler = BotReloadHandler(bot_file)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()
    print("👀 Observando mudanças em bot.py. Pressione Ctrl+C para parar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("⛔ Interrompido manualmente.")

    observer.join()
