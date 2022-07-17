from data import ADMIN_IDS, WEBHOOK_PATH, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT 
from loader import bot
from middlewares import setup_middlewares
from filters import setup_filters
from handlers import dp
from aiogram import executor
from utils.db import create_tables


async def on_startup(dp):
    await create_tables()
    setup_middlewares(dp)
    setup_filters(dp)
    for admin in ADMIN_IDS:
        await bot.send_message(admin, "Bot started working")
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup)
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )