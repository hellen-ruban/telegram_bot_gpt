import asyncio
from logging.config import dictConfig
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from src.settings.config import TG_BOT_API_KEY, LOGS_DIR
from src.bot.handlers.start import start
from src.bot.handlers.random import random_fact
from src.bot.handlers.callbacks import on_callback
from src.bot.keyboards import CB_FINISH, CB_MORE
from src.bot.handlers.gpt import build_gpt_conv_handler
from src.bot.handlers.talk import build_talk_conv_handler


def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    dictConfig({
        "version": 1,
        "formatters": {"std": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "std", "level": "INFO"},
            "file": {
                "class": "logging.FileHandler",
                "filename": LOGS_DIR / "app.log",
                "encoding": "utf-8",
                "formatter": "std",
                "level": "INFO",
            },
        },
        "root": {"handlers": ["console", "file"], "level": "INFO"},
    })

def build_app():
    # TG_BOT_API_KEY береться з os.environ у config.py
    return ApplicationBuilder().token(TG_BOT_API_KEY).build()

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_fact))
    app.add_handler(CallbackQueryHandler(on_callback, pattern=f"^({CB_FINISH}|{CB_MORE})$"))

    app.add_handler(build_gpt_conv_handler())
    app.add_handler(build_talk_conv_handler())

def run():
    setup_logging()
    app = build_app()
    register_handlers(app)
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except RuntimeError:
        # якщо середовище вже створило цикл (інколи в IDE) — запускаємо напряму
        run()



"""import os
from src.settings.config import TG_BOT_API_KEY
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler
#from utils import load_messages_for_bot
from openai import OpenAI

    async def start(update:Update, context:ContextTypes):
        text = load_messages_for_bot("main")
        await update.message.reply_text(text)



    app = ApplicationBuilder().token(TG_BOT_API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random))

    app.run_polling()

if __name__ == "__main__":
    main()"""