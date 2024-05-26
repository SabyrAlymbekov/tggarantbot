from aiogram import Bot, Dispatcher

import config
import asyncio
from app.handler import router

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')