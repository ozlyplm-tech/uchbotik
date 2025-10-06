import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

app = Flask(__name__)

# --- handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я УчБотик 🤖 Пришли текст или фото задачи.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Принял текст ✅. Скоро будет подробный разбор!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получил ✅. Анализ картинок добавим позже.")

def run_bot():
    bot = ApplicationBuilder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot.run_polling()

# --- health-check для Render ---
@app.get("/")
def health():
    return "ok", 200

_started = False
@app.before_first_request
def _start():
    global _started
    if not _started:
        threading.Thread(target=run_bot, daemon=True).start()
        _started = True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
