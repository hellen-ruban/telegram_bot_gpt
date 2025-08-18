import os
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
    main()