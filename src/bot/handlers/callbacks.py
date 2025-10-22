from telegram import Update, InputFile
from telegram.ext import ContextTypes
from src.bot.keyboards import CB_FINISH, CB_MORE, random_keyboard
from src.settings.config import MESSAGES_DIR, IMAGES_DIR, PROMPTS_DIR
from src.services.chatgpt import ask_short

RANDOM_IMG = IMAGES_DIR / "random.jpg"
RANDOM_PROMPT = PROMPTS_DIR / "random.txt"

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()

    if q.data == CB_FINISH:
        start_text = (MESSAGES_DIR / "main.html").read_text(encoding="utf-8")
        await q.message.reply_text(start_text) # можно добавить  parse_mode="HTML" (в дужки) что б использовать хтмл
        return

    if q.data == CB_MORE:
        prompt = RANDOM_PROMPT.read_text(encoding="utf-8").strip()
        answer = await ask_short(prompt)
        with RANDOM_IMG.open("rb") as f:
            await q.message.reply_photo(
                photo=InputFile(f),
                caption=answer,
                reply_markup=random_keyboard(),
            )
