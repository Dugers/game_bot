from loader import dp
from utils.db import get_games
from keyboards.default import main_menu_keyboard
from aiogram.types import Message
from .game.multiplayer_games import join_in_game


@dp.message_handler(commands=['start'])
async def start(message: Message, state):
    if message.text != "/start":
        user_data = message.text.replace("/start ", "")
        if "join" in user_data:
            try:
                room_id = int(user_data.replace(" ", "").replace("_", "").replace("join", ""))
                game = await get_games(game_id=room_id)
                if game is None:
                    await message.answer("Игровой комнаты с таким ID не существует", reply_markup=main_menu_keyboard)
                    return
                elif game['status'] == True:
                    await message.answer("Игра уже закончена", reply_markup=main_menu_keyboard)
                    return
                await message.answer("Отправляю вас в комнату", reply_markup=main_menu_keyboard)
                await join_in_game(message, state, game_room_id=room_id, user_id=message.chat.id)
                return
            except:
                await message.answer("ID комнаты указан не верно", reply_markup=main_menu_keyboard)
                return
    await message.answer("Привет, я игровой бот")
    await message.answer_sticker("CAACAgEAAxkBAAEFR95i0QdrYQq0Bmz8uhDcdbGjoS58OgACDwEAAjgOghG1zE1_4hSRgikE")
    await message.answer("Перед тобой представлено меню, давай начнем")
    await message.answer('Кнопка "Мой профиль" отправит тебя в твой профиль\nКнопка "Играть" отправит тебя в игровое меню\nКнопка "Поделиться" расскажет как пригласить пользователя в комнату', reply_markup=main_menu_keyboard)