import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

PORT = int(os.getenv("PORT", "10000"))
# Render сам выставляет эту переменную с твоим публичным URL (например https://uchbotik.onrender.com)
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL")
if not PUBLIC_URL:
    # если вдруг переменной нет, можно захардкодить свой URL:
    # PUBLIC_URL = "https://uchbotik.onrender.com"
    raise RuntimeError("RENDER_EXTERNAL_URL is not set")

# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я УчБотик 🤖 Пришли текст или фото задачи.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Принял текст ✅. Скоро будет подробный разбор!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получил ✅. Анализ картинок добавим позже.")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ---------- aiohttp-приложение для вебхука + health ----------
    web_app = web.Application()

    # health-check для Render (HEAD/GET на "/")
    async def health(request: web.Request):
        return web.Response(text="ok")
    web_app.router.add_get("/", health)
    web_app.router.add_head("/", health)

    # Пусть вебхук ходит на https://<твой-домен>/<токен>
    webhook_path = f"/{TOKEN}"
    webhook_url = f"{PUBLIC_URL}{webhook_path}"

    # 1) регистрируем вебхук в Telegram
    await application.bot.set_webhook(url=webhook_url)

    # 2) запускаем webhook-сервер (PTB сам принимает POST от Telegram)
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,      # тот же путь, что и в webhook_url
        webhook_url=webhook_url,
        web_app=web_app,     # даём наш aiohttp app (там обработчик "/" для Render)
        drop_pending_updates=True
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
