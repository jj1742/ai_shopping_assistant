from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

request_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Начать", callback_data="request")]]
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новый запрос")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Сделать новый запрос",
)
