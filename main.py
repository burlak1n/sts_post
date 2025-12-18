import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

from sql import add_user, confirm_user, init_db, is_confirmed

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    user = message.from_user
    add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить участие", callback_data="confirm")]
        ]
    )

    await message.answer(
        "Привет! Подтверди участие в Первой Новогодней Почте Ингруп СтС",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data == "confirm")
async def button_callback(callback: CallbackQuery):
    await callback.answer()

    if not is_confirmed(callback.from_user.id):
        confirm_user(callback.from_user.id)
        await callback.message.edit_text("Супер, ты записан! Жди сообщений")
    else:
        await callback.message.edit_text("Ты уже записан!")


async def main():
    init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
