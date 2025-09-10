from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Ariza topshirish", callback_data="apply"),
            InlineKeyboardButton(text="ℹ️ Dastur haqida", callback_data="about"),
        ],
        [
            InlineKeyboardButton(text="📊 Mening natijam", callback_data="my_result"),
            InlineKeyboardButton(text="❓ Yordam", callback_data="help"),
        ]
    ]
)
