import argparse
import asyncio
import logging
import os
import sqlite3

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = "users.db"


def get_all_senders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT telegram_id_sender FROM distribution")
    senders = [row[0] for row in cursor.fetchall()]
    conn.close()
    return senders


async def send_reminder_messages(test_mode: bool = False):
    bot = Bot(token=BOT_TOKEN)
    
    if test_mode:
        senders = [870424192, 1291534395]
        logger.info("Режим тестирования: отправка только тестовым пользователям")
    else:
        senders = get_all_senders()
        logger.info(f"Найдено {len(senders)} отправителей в распределении")
    senders = [284680089, 443649079, 477151236, 483885670, 544582975, 580039404, 589343617, 606231042, 695703825, 725755418, 796402754, 803340918, 803884567, 816519598, 833897132, 839244906, 853384281, 870424192, 923346122, 934490275, 961340091, 976155349, 980862746, 992983041, 1291534395, 1293946627, 1481624168, 1851170300, 2020158689, 5163857098]
    print(f"\nСписок ID на рассылку ({len(senders)} человек):")
    print(senders)
    print()
    message_text = (
        "Совсем скоро корпорат, а значит и почта!\n\n"
        "Как отправить письмо:\n"
        "1. Положить письма на точке почты\n"
        "2. Отсканировать кьюар и отметить в боте, кому отправил письма\n\n"
        "Письмо обязательно должно быть в конверте, если что они будут на точке, с подписанным именем и фамилией АДРЕСАТА\n\n"
        "Как получить письмо:\n"
        "1. Получаешь уведомление, что письмо пришло\n"
        "2. Забираешь на точке"
    )
    
    success_count = 0
    error_count = 0
    
    for i, user_id in enumerate(senders, 1):
        try:
            await bot.send_message(chat_id=user_id, text=message_text, request_timeout=15)
            logger.info(f"[{i}/{len(senders)}] Сообщение отправлено пользователю {user_id}")
            success_count += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"[{i}/{len(senders)}] Ошибка при отправке сообщения пользователю {user_id}: {e}")
            error_count += 1
            await asyncio.sleep(1)
    
    print(f"\n✅ Успешно отправлено: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    
    await bot.session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Отправить только тестовым пользователям")
    args = parser.parse_args()
    
    asyncio.run(send_reminder_messages(test_mode=args.test))

