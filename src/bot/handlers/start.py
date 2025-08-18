from telegram import Update
from telegram.ext import ContextTypes
from src.settings.config import MESSAGES_DIR

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (MESSAGES_DIR / "main.html").read_text(encoding="utf-8")
    await update.message.reply_text(text, parse_mode="HTML")
