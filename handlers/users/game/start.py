from loader import dp
from aiogram.types import Message, CallbackQuery
from keyboards.inline import select_game_keyboard
from .bot_games import game_mode_bot_start
from .multiplayer_games import game_mode_multiplayer_start


@dp.message_handler(lambda message: message.text.lower() == "играть")
async def select_play_mode(message: Message):
    await message.answer("Выберите режим игры", reply_markup=select_game_keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith('game_mode_'))
async def send_in_games_list(callback: CallbackQuery):
    await callback.message.delete()
    game_mode = callback.data.replace("game_mode_", "")
    if game_mode == "bot":
        await game_mode_bot_start(callback.message)
        return
    elif game_mode == "multiplayer":
        await game_mode_multiplayer_start(callback.message)
        return


@dp.callback_query_handler(text="cancel_games_list")
async def cancel_games_list(callback: CallbackQuery):
    await callback.message.delete()
    await select_play_mode(callback.message)