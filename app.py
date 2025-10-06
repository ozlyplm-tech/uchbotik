import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- настройки ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")
PORT = int(os.getenv("PORT", "10000"))

# --- health-check HTTP server на $PORT (для Render) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"ok")

def start_health_server():
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()

# --- Telegram handlers (async — это норм для PTB v21) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я УчБотик 🤖 Пришли текст или фото задачи.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Принял текст ✅. Скоро будет подробный разбор!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получил ✅. Анализ картинок добавим позже.")

def main():
    # поднимаем health-сервер в фоне
    threading.Thread(target=start_health_server, daemon=True).start()

    # собираем и запускаем Телеграм-бот
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ВАЖНО: синхронный запуск без asyncio.run и без сигналов
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
