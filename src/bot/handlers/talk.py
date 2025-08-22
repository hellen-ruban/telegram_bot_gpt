from telegram import Update, InputFile
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from src.settings.config import IMAGES_DIR, PROMPTS_DIR, MESSAGES_DIR
from src.services.chatgpt import ask_chat
from src.bot.keyboards import (
    talk_menu_keyboard, talk_end_keyboard,
    CB_TALK_END,
    CB_TALK_SEL_COBAIN, CB_TALK_SEL_HAWKING, CB_TALK_SEL_NIETZSCHE,
    CB_TALK_SEL_QUEEN, CB_TALK_SEL_TOLKIEN,
)

# СТАНИ розмови
TALK_CHOOSE = 30
TALK_CHAT   = 31

# Картинка для старту режиму /talk
TALK_IMG = IMAGES_DIR / "talk.jpg"

# Картинки для кожної особистості
PERSONA_IMAGES = {
    "cobain":    IMAGES_DIR / "talk_cobain.jpg",
    "hawking":   IMAGES_DIR / "talk_hawking.jpg",
    "nietzsche": IMAGES_DIR / "talk_nietzsche.jpg",
    "queen":     IMAGES_DIR / "talk_queen.jpg",
    "tolkien":   IMAGES_DIR / "talk_tolkien.jpg",
}

# Людські назви персонажів
PERSONA_TITLES = {
    "cobain":    "Курт Кобейн",
    "hawking":   "Стівен Гокінг",
    "nietzsche": "Фрідріх Ніцше",
    "queen":     "Королева Елизавета ІІ",
    "tolkien":   "Дж. Р. Р. Толкін",
}

def _persona_key_from_callback(cb_data: str) -> str:
    # "talk_cobain" -> "cobain"
    return cb_data.replace("talk_", "", 1)

def _load_persona_prompt(key: str) -> str:
    # шукаємо resources/prompts/talk_<key>.txt; якщо нема — даємо дефолт
    p = PROMPTS_DIR / f"talk_{key}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()

    defaults = {
        "cobain": (
            "Ти відповідаєш голосом Курта Кобейна українською мовою. "
            "Стиль — музичний, чутливий, інколи іронічний, без токсичності."
        ),
        "hawking": (
            "Ти — Стівен Гокінг. Пояснюй науку зрозуміло, спокійно, з повагою до співрозмовника."
        ),
        "nietzsche": (
            "Ти — Фрідріх Ніцше. Відповідай афористично, філософськи, не переходь у зневагу."
        ),
        "queen": (
            "Ти — Королева Елизавета ІІ. Правителька Великої Британії, стримана, коректна та велична."
        ),
        "tolkien": (
            "Ти — Дж. Р. Р. Толкін. Відповідай образно, але лаконічно; фантазійні алюзії доречні."
        ),
    }
    return defaults[key]

def _ensure_history(context: ContextTypes.DEFAULT_TYPE) -> list[dict]:
    hist = context.user_data.get("talk_history")
    if not isinstance(hist, list):
        hist = []
        context.user_data["talk_history"] = hist
    return hist

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # надішлемо стартову картинку
    try:
        with TALK_IMG.open("rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
    except FileNotFoundError:
        pass

    # текст-запрошення (якщо є resources/messages/talk.txt)
    msg_path = MESSAGES_DIR / "talk.txt"
    intro = msg_path.read_text(encoding="utf-8") if msg_path.exists() else "Оберіть відому особистість:"
    context.user_data.pop("talk_history", None)
    context.user_data.pop("talk_persona", None)

    await update.message.reply_text(intro, reply_markup=talk_menu_keyboard())
    return TALK_CHOOSE

async def talk_choose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    if q.data == CB_TALK_END:
        start_path = MESSAGES_DIR / "main.html"
        start_text = start_path.read_text(encoding="utf-8") if start_path.exists() else "Повернулись на старт. /start"
        await q.message.reply_text(start_text)
        return ConversationHandler.END

    key = _persona_key_from_callback(q.data)  # cobain/hawking/nietzsche/queen/tolkien
    context.user_data["talk_persona"] = key

    # ставимо системний промпт
    prompt = _load_persona_prompt(key)
    context.user_data["talk_history"] = [{"role": "system", "content": prompt}]

# NEW: надсилаємо аватарку обраної особистості + підпис
    img_path = PERSONA_IMAGES.get(key)
    title = PERSONA_TITLES.get(key, "Відома особистість")
    if img_path and img_path.exists():
        with img_path.open("rb") as f:
            await q.message.reply_photo(
                photo=InputFile(f),
                caption=f"Спілкуємось як {title}. Напишіть перше повідомлення."
            )
    else:
        # запасний варіант, якщо зображення відсутнє
        await q.message.reply_text(f"Спілкуємось як {title}. Напишіть перше повідомлення.")

    return TALK_CHAT

async def talk_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Надішліть текстове повідомлення.", reply_markup=talk_end_keyboard())
        return TALK_CHAT

    hist = _ensure_history(context)
    if not hist or hist[0].get("role") != "system":
        key = context.user_data.get("talk_persona", "cobain")
        hist[:] = [{"role": "system", "content": _load_persona_prompt(key)}]

    hist.append({"role": "user", "content": text})
    answer = await ask_chat(hist)
    hist.append({"role": "assistant", "content": answer})

    await update.message.reply_text(answer, reply_markup=talk_end_keyboard())
    return TALK_CHAT

async def talk_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    if q.data == CB_TALK_END:
        context.user_data.pop("talk_history", None)
        context.user_data.pop("talk_persona", None)
        start_path = MESSAGES_DIR / "main.html"
        start_text = start_path.read_text(encoding="utf-8") if start_path.exists() else "Повернулись на старт. /start"
        await q.message.reply_text(start_text)
        return ConversationHandler.END
    return TALK_CHAT

async def talk_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("talk_history", None)
    context.user_data.pop("talk_persona", None)
    start_path = MESSAGES_DIR / "main.html"
    start_text = start_path.read_text(encoding="utf-8") if start_path.exists() else "Повернулись на старт. /start"
    await update.message.reply_text(start_text)
    return ConversationHandler.END

def build_talk_conv_handler() -> ConversationHandler:
    pattern_select = (
        f"^({CB_TALK_SEL_COBAIN}|{CB_TALK_SEL_HAWKING}|{CB_TALK_SEL_NIETZSCHE}|"
        f"{CB_TALK_SEL_QUEEN}|{CB_TALK_SEL_TOLKIEN}|{CB_TALK_END})$"
    )
    return ConversationHandler(
        entry_points=[CommandHandler("talk", talk_start)],
        states={
            TALK_CHOOSE: [CallbackQueryHandler(talk_choose, pattern=pattern_select)],
            TALK_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, talk_message),
                CallbackQueryHandler(talk_callbacks, pattern=f"^{CB_TALK_END}$"),
            ],
        },
        fallbacks=[CommandHandler("endtalk", talk_end)],
        allow_reentry=True,
    )
