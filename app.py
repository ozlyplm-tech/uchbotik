import os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

PORT = int(os.getenv("PORT", "10000"))

# ---------- health-check HTTP server (для Render) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

# ---------- Telegram handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я УчБотик 🤖 Пришли текст или фото задачи.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Принял текст ✅. Скоро будет подробный разбор!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получил ✅. Анализ картинок добавим позже.")

async def bot_main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    await app.run_polling()  # бот в главном потоке, сигналы ок

if __name__ == "__main__":
    # health-сервер на $PORT в отдельном потоке
    threading.Thread(target=start_health_server, daemon=True).start()
    # бот в главном потоке
    asyncio.run(bot_main())
