import asyncio
from telegram import Bot

async def send_telegram_message(message):
    bot_token = ''
    chat_id = ''
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

async def main():
    message = "ATENÇÃO AOS SINAIS"
    await send_telegram_message(message)

asyncio.run(main())