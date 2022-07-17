from loader import dp
from filters import UserInputFilter
from states import UserUpdateProfileState
from utils.db import update_user, get_games
from keyboards.inline import profile_menu_keyboard, cancel_keyboard, games_history_keyboard
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

@dp.message_handler(lambda message: message.text.lower() == "мой профиль")
async def user_profile(message: Message, user_info):
    games_count = await get_games(count=True, telegram_id=message.chat.id)
    games_count = games_count['count']
    await message.answer(f"Никнейм: {user_info['name']}\nКоличество игр: {games_count}\nКоличество побед: {user_info['wins']}\nКоличество поражение: {user_info['losses']}\nКоличество ничьих: {games_count - user_info['wins'] - user_info['losses']}\nПримечание:\nСтатистика ведется только по играм в кооперативном режиме", reply_markup=profile_menu_keyboard)


@dp.callback_query_handler(text="update_name")
async def user_update_set_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    msg = await callback.message.answer("Введите новый никнейм", reply_markup=cancel_keyboard("Отмена"))
    await UserUpdateProfileState.name.set()
    async with state.proxy() as data:
        data['msg'] = msg


@dp.message_handler(UserInputFilter(type="name"), state=UserUpdateProfileState.name)
async def user_update_name(message: Message, state: FSMContext, user_info):
    async with state.proxy() as data:
        await data['msg'].delete()
    await state.finish()
    await update_user(message.from_user.id, name=message.text)
    user_info = {'id': user_info['id'], 'name': message.text, 'telegram_id': user_info['telegram_id'], 'wins': user_info['wins'], 'losses': user_info['losses']}
    await message.answer("Никнейм успешно изменен")
    await user_profile(message, user_info)


@dp.message_handler(UserInputFilter(type="name", invalid=True), state=UserUpdateProfileState.name)
async def user_invalid_update_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await data['msg'].delete()
        data['msg'] = await message.answer("Никнейм введен неправильно\nВозможные причины:\nСодержит одни цифры\nСодержит @ или / \nСлишком короткий или слишком длинный", reply_markup=cancel_keyboard("Отмена"))


@dp.callback_query_handler(text="cancel", state=UserUpdateProfileState)
async def user_cancel_update(callback: CallbackQuery, state: FSMContext, user_info):
    await callback.message.delete()
    await state.finish()
    await user_profile(callback.message, user_info)


@dp.callback_query_handler(text="games_history")
async def user_games_history(callback: CallbackQuery, offset=0):
    try:
        await callback.message.delete()
    except:
        pass
    games_list = await get_games(user_games=True, telegram_id=callback.from_user.id, offset=offset)
    if len(games_list) == 0:
        await callback.message.answer("Вы пока не сыграли ни одной игры", reply_markup=cancel_keyboard("Вернуться обратно", "cancel_games_history"))
        return
    next_step_games_list = await get_games(user_games=True, telegram_id=callback.from_user.id, offset=offset+5)
    back_step = True
    next_step = True
    if offset == 0:
        back_step = False
    if len(next_step_games_list) == 0:
        next_step = False
    keyboard = games_history_keyboard(offset=offset, next_step=next_step, back_step=back_step)
    text = "ID | Тип игры | Статус"
    for game in games_list:
        status = "Проигрыш"
        if game['winner'] is None:
            status="Ничья"
        elif game['winner'] == callback.from_user.id:
            status="Победа"
        if game['game_type'] == "dice":
            game_type = "Кости"
        elif game['game_type'] == "dart":
            game_type = "Дартс"
        elif game['game_type'] == "bowling":
            game_type = "Боулинг"
        elif game['game_type'] == "basketball":
            game_type = "Баскетбол"
        elif game['game_type'] == "football":
            game_type = "Футбол"
        text += f"\n{game['id']} | {game_type} | {status}"
    await callback.message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith("games_history_step"))
async def games_history_pagination(callback: CallbackQuery):
    await callback.message.delete()
    await user_games_history(callback, offset=int(callback.data.replace("games_history_step_", "")))


@dp.callback_query_handler(text="cancel_games_history")
async def user_cancel_show_games_history(callback: CallbackQuery, user_info):
    await callback.message.delete()
    await user_profile(callback.message, user_info)