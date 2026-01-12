import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

from sql import (
    add_user,
    confirm_user,
    init_db,
    is_confirmed,
    get_recipients_for_sender,
    get_user_contact,
    update_distribution_status,
    take_letters_for_recipient,
    get_pending_letters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_IDS = {1291534395, 870424192}


async def send_delayed_notification(recipient_id: int, sender_contact: str, delay: int):
    await asyncio.sleep(delay)
    try:
        message_text = (
            "<b>Получено новое письмо</b>\n"
            "Подойди на точку к Роме и Милане, чтобы забрать его!"
        )
        await bot.send_message(chat_id=recipient_id, text=message_text, parse_mode="HTML")
        logger.info(f"Уведомление отправлено получателю {recipient_id} через {delay} сек")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления получателю {recipient_id}: {e}")


@dp.message(Command("take"))
async def take(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Использование: /take <telegram_id>")
        return

    try:
        recipient_id = int(parts[1])
    except ValueError:
        await message.answer("telegram_id должен быть числом")
        return

    senders = take_letters_for_recipient(recipient_id)
    if not senders:
        await message.answer("Нет писем со статусом 1 для этого пользователя.")
        return

    recipient_contact = get_user_contact(recipient_id)
    for sender_id in senders:
        try:
            await bot.send_message(sender_id, f"{recipient_contact} забрал твоё письмо!")
        except Exception:
            pass

    await message.answer(f"Готово. Отмечено: {len(senders)}")


@dp.message(Command("pending"))
async def pending(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    rows = get_pending_letters()
    if not rows:
        await message.answer("Нет писем со статусом 1.")
        return

    def fmt_contact(username, first_name, last_name):
        if username:
            return f"@{username}" if not username.startswith("@") else username
        return f"{first_name} {last_name or ''}".strip()

    chunks = []
    cur = ""
    for i, (sid, su, sf, sl, rid, ru, rf, rl) in enumerate(rows, start=1):
        line = f"{i}. {sid} ({fmt_contact(su, sf, sl)}) -> {rid} ({fmt_contact(ru, rf, rl)})\n"
        if len(cur) + len(line) > 3900:
            chunks.append(cur)
            cur = ""
        cur += line
    if cur:
        chunks.append(cur)

    for text in chunks:
        await message.answer(text)


@dp.message(Command("start"))
async def start(message: Message):
    user = message.from_user
    add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    start_param = args[0] if args else None

    if start_param == "resetcorporate":
        recipients = get_recipients_for_sender(user.id)
        if not recipients:
            await message.answer("У тебя нет подопечных для сброса.")
            return

        for recipient_id, _, _, _, _ in recipients:
            update_distribution_status(user.id, recipient_id, 0)

        await message.answer("Готово: всем подопечным выставлен статус 0.")
        return

    if start_param == "corporate26":
        recipients = get_recipients_for_sender(user.id)
        if not recipients:
            await message.answer("У тебя нет получателей для отметки.")
            return

        keyboard_buttons = []
        for recipient_id, first_name, last_name, username, status in recipients:
            if status == 2:
                continue
            contact = get_user_contact(recipient_id)
            checked = "✓ " if status == 1 else ""
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{checked}{contact}",
                    callback_data=f"toggle_{recipient_id}"
                )
            ])

        if keyboard_buttons:
            keyboard_buttons.append([
                InlineKeyboardButton(text="Подтвердить", callback_data="confirm_letters")
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        text = "Привет! Отметь людей, чьи письма ты кладёшь:\n"
        for recipient_id, _, _, _, status in recipients:
            contact = get_user_contact(recipient_id)
            if status == 1:
                text += f"{contact} (отправлено)\n"
            elif status == 2:
                text += f"{contact} (получено)\n"
            else:
                text += f"{contact}\n"

        await message.answer(text, reply_markup=keyboard)
        return
    else:
        return
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить участие", callback_data="confirm")]
            ]
        )

        await message.answer(
            "Привет! Это первая Новогодняя почта Ингруп СтС!\n\n"
            "После регистрации пройдет жеребьевка, и ты получишь список СтСников, которые тоже учавствуют в почте. Именно они будут ждать твоего письма!\n"
            "Письма приносишь на корпорат и, получив уведомление, забираешь свои.\n\n"
            "Если не сможешь приехать на корпорат, то передай письма Милане или Роме (@andibka, @burlak1n)\n\n"
            "Дд регистрации 22 декабря 23:59\n\n"
            "По любым вопросам:\n"
            "@andibka | @burlak1n\n\n"
            "Для участия, нажми на кнопку ниже!",
            reply_markup=keyboard,
        )


@dp.callback_query(F.data == "confirm")
async def button_callback(callback: CallbackQuery):
    await callback.answer()

    if not is_confirmed(callback.from_user.id):
        confirm_user(callback.from_user.id)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Супер, ты зарегистрирован! Жди сообщений!")
    else:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Ты уже записан!")


@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_recipient(callback: CallbackQuery):
    recipient_id = int(callback.data.split("_")[1])
    sender_id = callback.from_user.id

    recipients = get_recipients_for_sender(sender_id)
    recipient_data = next((r for r in recipients if r[0] == recipient_id), None)
    
    if not recipient_data:
        await callback.answer("Получатель не найден", show_alert=True)
        return

    current_status = recipient_data[4]
    new_status = 1 if current_status == 0 else 0
    update_distribution_status(sender_id, recipient_id, new_status)

    keyboard_buttons = []
    recipients = get_recipients_for_sender(sender_id)
    for rec_id, first_name, last_name, username, status in recipients:
        if status == 2:
            continue
        contact = get_user_contact(rec_id)
        checked = "✓ " if status == 1 else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{checked}{contact}",
                callback_data=f"toggle_{rec_id}"
            )
        ])

    if keyboard_buttons:
        keyboard_buttons.append([
            InlineKeyboardButton(text="Подтвердить", callback_data="confirm_letters")
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "confirm_letters")
async def confirm_letters(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
    sender_id = callback.from_user.id
    sender_contact = get_user_contact(sender_id)
    
    recipients = get_recipients_for_sender(sender_id)
    marked_recipients = [r for r in recipients if r[4] == 1]
    
    if marked_recipients:
        for recipient_id, _, _, _, _ in marked_recipients:
            delay = random.randint(30, 120)
            asyncio.create_task(send_delayed_notification(recipient_id, sender_contact, delay))
            update_distribution_status(sender_id, recipient_id, 1)
        
        await callback.message.answer(
            f"Спасибо за участие! Уведомления будут отправлены {len(marked_recipients)} получателям в течение 2 минут."
        )
    else:
        await callback.message.answer(
            "Спасибо за участие!"
        )


async def main():
    init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
