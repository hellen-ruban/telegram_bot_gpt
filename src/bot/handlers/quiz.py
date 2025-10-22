from telegram import Update, InputFile
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from src.settings.config import IMAGES_DIR, PROMPTS_DIR, MESSAGES_DIR
from src.services.chatgpt import ask_chat
from src.bot.keyboards import (
    quiz_topics_keyboard, quiz_actions_keyboard,
    CB_QUIZ_TOPIC_HISTORY, CB_QUIZ_TOPIC_MATH, CB_QUIZ_TOPIC_BIOLOGY,
    CB_QUIZ_MORE, CB_QUIZ_CHANGE, CB_QUIZ_END,
)

# СТАНИ
QUIZ_CHOOSE = 60
QUIZ_WAIT_ANSWER = 61

QUIZ_IMG = IMAGES_DIR / "quiz.jpg"
QUIZ_PROMPT = PROMPTS_DIR / "quiz.txt"

# Системний промпт (якщо файлу немає)
DEFAULT_SYSTEM_PROMPT = (
    "Зараз я буду просити тебе генерувати питання для квізу.\n"
    "Якщо я напишу 'quiz_history', потрібно згенерувати 1 питання на тему всесвітньої історії зі шкільної програми.\n"
    "Якщо я напишу 'quiz_math', потрібно згенерувати 1 питання на тему математичних теорій зі шкільної програми\n"
    "Якщо я напишу 'quiz_biology', потрібно згенерувати 1 питання на тему біології, зоології, анатомії зі шкільної програми.\n"
    "Якщо я напишу \"quiz_more\", потрібно згенерувати інше 1 питання на ту ж тему, що й попереднє.\n"
    "Відповіді на ці питання мають бути короткими - максимум кілька слів.\n"
    "Якщо я напишу правильну відповідь або дуже схожу на правильну, ти маєш відповісти \"Правильно!\"\n"
    "Якщо відповідь неправильна - ти маєш відповісти в наступному форматі:\n"
    "\"Неправильно! Правильна відповідь - {answer}\", де {answer} - та відповідь, яку ти вважаєш правильною.\n"
    "Не задавай питання, де відповідь - числове значення. Тільки слова."
)

def _load_system_prompt() -> str:
    p = PROMPTS_DIR / "quiz.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return DEFAULT_SYSTEM_PROMPT

def _ensure_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    ud = context.user_data
    ud.setdefault("quiz_history", [])
    ud.setdefault("quiz_topic_key", None)  # 'history' | 'math' | 'biology'
    ud.setdefault("quiz_score_correct", 0)
    ud.setdefault("quiz_score_total", 0)

def _topic_cmd_by_callback(cb_data: str) -> str:
    """Перетворюємо callback у команду для GPT згідно з промптом."""
    if cb_data == CB_QUIZ_TOPIC_HISTORY:
        return "quiz_history"
    if cb_data == CB_QUIZ_TOPIC_MATH:
        return "quiz_math"
    if cb_data == CB_QUIZ_TOPIC_BIOLOGY:
        return "quiz_biology"
    return "quiz_history"

def _topic_key_by_cmd(cmd: str) -> str:
    return cmd.replace("quiz_", "", 1)  # 'quiz_history' -> 'history'

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ /quiz: показати картинку + меню тем, скинути стан. """
    try:
        with QUIZ_IMG.open("rb") as f:
            await update.message.reply_photo(photo=InputFile(f))
    except FileNotFoundError:
        pass

    _ensure_state(context)
    context.user_data["quiz_history"] = [{"role": "system", "content": _load_system_prompt()}]
    context.user_data["quiz_topic_key"] = None
    context.user_data["quiz_score_correct"] = 0
    context.user_data["quiz_score_total"] = 0

    intro_path = MESSAGES_DIR / "quiz.txt"
    intro = intro_path.read_text(encoding="utf-8") if intro_path.exists() else "Оберіть тему квізу:"
    await update.message.reply_text(intro, reply_markup=quiz_topics_keyboard())
    return QUIZ_CHOOSE

async def quiz_choose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Клік по темі або Закінчити."""
    q = update.callback_query
    await q.answer()

    if q.data == CB_QUIZ_END:
        start_path = MESSAGES_DIR / "main.html"
        start_text = start_path.read_text(encoding="utf-8") if start_path.exists() else "Повернулися на старт. /start"
        await q.message.reply_text(start_text)
        return ConversationHandler.END

    # 1) Визначаємо команду для GPT за темою
    cmd = _topic_cmd_by_callback(q.data)  # 'quiz_history' | 'quiz_math' | 'quiz_biology'
    context.user_data["quiz_topic_key"] = _topic_key_by_cmd(cmd)  # 'history' | 'math' | 'biology'

    # 2) Просимо питання цієї теми
    hist = context.user_data["quiz_history"]
    hist.append({"role": "user", "content": cmd})
    question = await ask_chat(hist)
    hist.append({"role": "assistant", "content": question})

    await q.message.reply_text(question)
    return QUIZ_WAIT_ANSWER

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Користувач відповідає на питання → GPT оцінює → рахуємо бал → показуємо кнопки дій."""
    user_answer = (update.message.text or "").strip()
    if not user_answer:
        await update.message.reply_text("Надішліть текстову відповідь.")
        return QUIZ_WAIT_ANSWER

    hist = context.user_data.get("quiz_history", [])
    if not hist:
        # на всякий — переініціалізуємо
        hist[:] = [{"role": "system", "content": _load_system_prompt()}]
        context.user_data["quiz_topic_key"] = None

    # Відповідь користувача → GPT (промпт каже як відповідати: "Правильно!" / "Неправильно! ...")
    hist.append({"role": "user", "content": user_answer})
    evaluation = await ask_chat(hist)
    hist.append({"role": "assistant", "content": evaluation})

    # Рахунок: якщо GPT почав з "Правильно!"
    context.user_data["quiz_score_total"] += 1
    if evaluation.strip().startswith("Правильно!"):
        context.user_data["quiz_score_correct"] += 1

    score = f"Рахунок: {context.user_data['quiz_score_correct']} з {context.user_data['quiz_score_total']}"
    await update.message.reply_text(f"{evaluation}\n\n{score}", reply_markup=quiz_actions_keyboard())
    return QUIZ_WAIT_ANSWER

async def quiz_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Кнопки: ще питання / змінити тему / закінчити."""
    q = update.callback_query
    await q.answer()

    if q.data == CB_QUIZ_END:
        start_path = MESSAGES_DIR / "main.html"
        start_text = start_path.read_text(encoding="utf-8") if start_path.exists() else "Повернулися на старт. /start"
        await q.message.reply_text(start_text)
        return ConversationHandler.END

    if q.data == CB_QUIZ_CHANGE:
        await q.message.reply_text("Оберіть іншу тему:", reply_markup=quiz_topics_keyboard())
        return QUIZ_CHOOSE

    if q.data == CB_QUIZ_MORE:
        # Надіслати сигнал GPT "quiz_more" (на ту ж тему)
        hist = context.user_data.get("quiz_history", [])
        if not hist:
            hist[:] = [{"role": "system", "content": _load_system_prompt()}]
        hist.append({"role": "user", "content": "quiz_more"})
        question = await ask_chat(hist)
        hist.append({"role": "assistant", "content": question})

        await q.message.reply_text(question)
        return QUIZ_WAIT_ANSWER

    return QUIZ_WAIT_ANSWER

def build_quiz_conv_handler() -> ConversationHandler:
    """Реєстрація сценарію /quiz."""
    pattern_topics = f"^({CB_QUIZ_TOPIC_HISTORY}|{CB_QUIZ_TOPIC_MATH}|{CB_QUIZ_TOPIC_BIOLOGY}|{CB_QUIZ_END})$"
    pattern_actions = f"^({CB_QUIZ_MORE}|{CB_QUIZ_CHANGE}|{CB_QUIZ_END})$"

    return ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz_start)],
        states={
            QUIZ_CHOOSE: [CallbackQueryHandler(quiz_choose, pattern=pattern_topics)],
            QUIZ_WAIT_ANSWER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer),
                CallbackQueryHandler(quiz_actions, pattern=pattern_actions),
            ],
        },
        fallbacks=[CommandHandler("endquiz", quiz_start)],
        allow_reentry=True,
    )
