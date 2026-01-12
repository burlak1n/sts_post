import argparse
import asyncio
import logging
import os

from aiogram import Bot
from dotenv import load_dotenv

from sql import get_confirmed_users, get_recipients_for_sender, get_user_contact

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def send_distribution_messages(test_mode: bool = False):
    bot = Bot(token=BOT_TOKEN)
    
    if test_mode:
        users = [870424192, 1291534395]
        logger.info("Режим тестирования: отправка только тестовым пользователям")
    else:
        users = get_confirmed_users()
    
    for user_id in users:
        recipients = get_recipients_for_sender(user_id)
        
        if not recipients:
            logger.warning(f"У пользователя {user_id} нет получателей")
            continue
        
        text = """Новогоднее настроение — это то, что мы создаем сами: когда покупаем подарки, слушаем новогоднюю музыку, планируем встречи… и пишем письма.

Те самые — новогодние, бумажные, в которые можно вложить весь свой креатив, самые добрые и важные слова за этот год и самые теплые пожелания на следующий!
<blockquote>А вот и твои адресаты Новогодней почты:
"""
        for recipient_id, first_name, last_name, username, status in recipients:
            contact = get_user_contact(recipient_id)
            text += f"{contact}\n"
        
        text += """</blockquote>Каждому из них напиши по письму и не забудь обязательно взять все на Корпорат"""
        
        try:
            await bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            logger.info(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    
    await bot.session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Отправить только пользователю 870424192")
    args = parser.parse_args()
    
    asyncio.run(send_distribution_messages(test_mode=args.test))

