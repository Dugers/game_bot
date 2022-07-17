from utils.db import get_users, create_user
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.middlewares import BaseMiddleware


class UserMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: Message, data):
        telegram_id = message.from_user.id
        user_info = await get_users(telegram_id)
        if user_info is None:
            count_users = await get_users(count=True)
            count_users = count_users['count']
            name = f"Player {count_users + 1}"
            await create_user(telegram_id, name)
            user_info = await get_users(telegram_id)
        data['user_info'] = user_info


    async def on_pre_process_callback_query(self, callback: CallbackQuery, data):
        await self.on_pre_process_message(callback, data)