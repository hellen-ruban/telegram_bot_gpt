from telegram import Update, InputFile
from telegram.ext import ContextTypes
from src.bot.keyboards import random_keyboard
from src.settings.config import IMAGES_DIR, PROMPTS_DIR
from src.services.chatgpt import ask_short

RANDOM_IMG = IMAGES_DIR / "random.jpg"
RANDOM_PROMPT = PROMPTS_DIR / "random.txt"

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 1) читаємо промпт із файлу
    prompt = RANDOM_PROMPT.read_text(encoding="utf-8").strip()

    # 2) запит до ChatGPT
    answer = await ask_short(prompt)

    # 3) надсилаємо зображення з підписом і кнопками
    with RANDOM_IMG.open("rb") as f:
        await update.message.reply_photo(
            photo=InputFile(f),
            caption=answer,
            reply_markup=random_keyboard(),
        )
