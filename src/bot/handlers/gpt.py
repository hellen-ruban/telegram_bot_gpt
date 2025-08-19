from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from src.settings.config import IMAGES_DIR
from src.services.chatgpt import ask_chat  # багатоходовий GPT

# стан розмови
GPT_CHAT = 1

# callback-дані для кнопок
CB_GPT_RESET = "gpt_reset"
CB_GPT_END = "gpt_end"

GPT_IMG = IMAGES_DIR / "gpt.jpg"   # зображення: src/resources/images/gpt.jpg


def _ensure_history(context: ContextTypes.DEFAULT_TYPE) -> list[dict]:
    hist = context.user_data.get("gpt_history")
    if not isinstance(hist, list):
        hist = []
        context.user_data["gpt_history"] = hist
    return hist


def _kb_gpt() -> InlineKeyboardMarkup:
    """Клавіатура під відповіддю GPT."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Очистити контекст", callback_data=CB_GPT_RESET)],
        [InlineKeyboardButton("Завершити діалог", callback_data=CB_GPT_END)],
    ])


async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ /gpt: надсилаємо картинку + інструкцію, входимо у стан GPT_CHAT. """
    try:
        with GPT_IMG.open("rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
    except FileNotFoundError:
        pass

    context.user_data["gpt_history"] = []
    await update.message.reply_text(
        "Напишіть повідомлення — відповідатиму як ChatGPT.",
        reply_markup=_kb_gpt()
    )
    return GPT_CHAT


async def gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Будь-яке текстове повідомлення у стані GPT_CHAT."""
    user_text = (update.message.text or "").strip()
    if not user_text:
        await update.message.reply_text("Надішліть, будь ласка, текст.", reply_markup=_kb_gpt())
        return GPT_CHAT

    history = _ensure_history(context)
    history.append({"role": "user", "content": user_text})

    answer = await ask_chat(history)
    history.append({"role": "assistant", "content": answer})

    await update.message.reply_text(answer, reply_markup=_kb_gpt())
    return GPT_CHAT


async def gpt_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка натискань на кнопки під відповідями."""
    q = update.callback_query
    await q.answer()

    if q.data == CB_GPT_RESET:
        context.user_data["gpt_history"] = []
        await q.message.reply_text("Контекст очищено. Пишіть далі.", reply_markup=_kb_gpt())
        return GPT_CHAT

    if q.data == CB_GPT_END:
        context.user_data.pop("gpt_history", None)
        await q.message.reply_text("Діалог /gpt завершено. Щоб почати знову — /gpt.")
        return ConversationHandler.END

    return GPT_CHAT


async def gpt_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Альтернативне завершення через команду /endgpt (необов’язково, але хай буде)."""
    context.user_data.pop("gpt_history", None)
    await update.message.reply_text("Діалог /gpt завершено.")
    return ConversationHandler.END


def build_gpt_conv_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("gpt", gpt_start)],
        states={
            GPT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_message),
                CallbackQueryHandler(gpt_callbacks, pattern=f"^({CB_GPT_RESET}|{CB_GPT_END})$"),
            ],
        },
        fallbacks=[CommandHandler("endgpt", gpt_end)],
        allow_reentry=True,
)
