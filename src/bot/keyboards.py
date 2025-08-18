from telegram import InlineKeyboardMarkup, InlineKeyboardButton

CB_FINISH = "finish"   # як /start
CB_MORE = "more"       # як /random

def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу ще факт", callback_data=CB_MORE)],
        [InlineKeyboardButton("Закінчити", callback_data=CB_FINISH)],
    ])
