from telegram import InlineKeyboardMarkup, InlineKeyboardButton

CB_FINISH = "finish"   # як /start
CB_MORE = "more"       # як /random

def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу ще факт", callback_data=CB_MORE)],
        [InlineKeyboardButton("Закінчити", callback_data=CB_FINISH)],
    ])

# ----- GPT -----
CB_GPT_RESET = "gpt_reset"
CB_GPT_END   = "gpt_end"

def gpt_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Очистити контекст", callback_data=CB_GPT_RESET)],
        [InlineKeyboardButton("Завершити діалог",  callback_data=CB_GPT_END)],
    ])

# ===== TALK (нове) =====
# Кнопки вибору особистості
CB_TALK_SEL_COBAIN    = "talk_cobain"
CB_TALK_SEL_HAWKING   = "talk_hawking"
CB_TALK_SEL_NIETZSCHE = "talk_nietzsche"
CB_TALK_SEL_QUEEN     = "talk_queen"
CB_TALK_SEL_TOLKIEN   = "talk_tolkien"

# Кнопка завершення саме для режиму talk
CB_TALK_END = "talk_end"

def talk_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Курт Кобейн",        callback_data=CB_TALK_SEL_COBAIN)],
        [InlineKeyboardButton("Стівен Гокінг",      callback_data=CB_TALK_SEL_HAWKING)],
        [InlineKeyboardButton("Фрідріх Ніцше",      callback_data=CB_TALK_SEL_NIETZSCHE)],
        [InlineKeyboardButton("Королева Елизавета ІІ",    callback_data=CB_TALK_SEL_QUEEN)],
        [InlineKeyboardButton("Дж. Р. Р. Толкін",   callback_data=CB_TALK_SEL_TOLKIEN)],
        [InlineKeyboardButton("Закінчити",          callback_data=CB_TALK_END)],
    ])

def talk_end_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Закінчити", callback_data=CB_TALK_END)]
    ])

# ===== MAIN MENU (нове) =====
CB_MENU_RANDOM = "menu_random"
CB_MENU_GPT    = "menu_gpt"
CB_MENU_TALK   = "menu_talk"

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Випадковий факт", callback_data=CB_MENU_RANDOM)],
        [InlineKeyboardButton("Чат з ChatGPT",   callback_data=CB_MENU_GPT)],
        [InlineKeyboardButton("Діалог з відомою особистістю", callback_data=CB_MENU_TALK)],
    ])

# ===== QUIZ (нове для промпта з командами) =====
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

CB_QUIZ_TOPIC_PROG     = "quiz_topic_prog"      # → відправимо GPT: quiz_prog
CB_QUIZ_TOPIC_MATH     = "quiz_topic_math"      # → відправимо GPT: quiz_math
CB_QUIZ_TOPIC_BIOLOGY  = "quiz_topic_biology"   # → відправимо GPT: quiz_biology

CB_QUIZ_MORE   = "quiz_more"     # → відправимо GPT: quiz_more
CB_QUIZ_CHANGE = "quiz_change"
CB_QUIZ_END    = "quiz_end"

def quiz_topics_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Python (програмування)", callback_data=CB_QUIZ_TOPIC_PROG)],
        [InlineKeyboardButton("Математика (теорії)",     callback_data=CB_QUIZ_TOPIC_MATH)],
        [InlineKeyboardButton("Біологія",               callback_data=CB_QUIZ_TOPIC_BIOLOGY)],
        [InlineKeyboardButton("Закінчити",                 callback_data=CB_QUIZ_END)],
    ])

def quiz_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу ще питання", callback_data=CB_QUIZ_MORE)],
        [InlineKeyboardButton("Змінити тему",    callback_data=CB_QUIZ_CHANGE)],
        [InlineKeyboardButton("Закінчити",       callback_data=CB_QUIZ_END)],
    ])
