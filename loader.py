from data import BOT_TOKEN, ADMIN_IDS
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage=MemoryStorage()
bot = Bot(BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)