from aiogram import Bot, Dispatcher
from utils.database import init_db
import config
import asyncio
from app.handler import router

bot = Bot(config.TOKEN)
dp = Dispatcher()
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')