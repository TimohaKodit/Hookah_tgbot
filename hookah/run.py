import asyncio
import logging
from bot_setup import bt
from aiogram import Bot, Dispatcher
from apps.database.models import async_main
from apps.handlers.admin_handlers import router as admin_router
from apps.handlers.master_handlers import router as master_router
from apps.handlers.user_handlers import router as user_router





async def main():
    await async_main()
    bot = bt
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(master_router)
    dp.include_router(user_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except:
        print('Exit')
        