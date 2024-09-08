import os 
import asyncio
from aiogram import Bot, Dispatcher, F

from app.handlers import router
from dotenv import load_dotenv


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
     try:
        asyncio.run(main())
     except KeyboardInterrupt:
        print('Bot is switched off')
    