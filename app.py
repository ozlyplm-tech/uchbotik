import os, threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

app = Flask(__name__)

# --- Telegram bot handlers ---
def start(update, context):
    update.message.reply_text("Привет! Я УчБотик 🤖 Напиши тему или пришли фото задачи.")

def handle_text(update, context):
    update.message.reply_text("Принял! Скоро научусь объяснять подробно ✍️")

def run_bot():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    updater.start_polling()
    updater.idle()

# --- Web health endpoint for Render ---
@app.get("/")
def health():
    return "ok", 200

# Запускаем Telegram-бот в отдельном потоке при старте веб-приложения
bot_thread_started = False
@app.before_first_request
def start_bot_thread():
    global bot_thread_started
    if not bot_thread_started:
        threading.Thread(target=run_bot, daemon=True).start()
        bot_thread_started = True

# Локальный запуск (не обязателен на Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
