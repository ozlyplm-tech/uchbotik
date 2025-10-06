from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update, context):
    update.message.reply_text("Привет! Я УчБотик 🤖 Напиши тему или пришли фото задачи.")

def handle_text(update, context):
    update.message.reply_text("Принял! Скоро научусь объяснять подробно ✍️")

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is not set")
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
