import os

from dotenv import load_dotenv
from telegram import Bot


async def send_telegram_message(message):
    load_dotenv()

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        raise RuntimeError(
            "Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no ambiente "
            "ou execute o programa com --dry-run."
        )

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)
