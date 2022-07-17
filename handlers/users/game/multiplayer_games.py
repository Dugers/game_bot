from loader import dp, bot
from states import MultiplayerGameState
from asyncio import sleep
from random import randint
from utils.db import get_games, create_game, get_users, update_game, update_user
from keyboards.inline import GamesListKeyboard, cancel_keyboard
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery


async def game_mode_multiplayer_start(message: Message, offset=0):
    games_list = await get_games(all_games=True, offset=offset)
    if len(games_list) == 0:
        keyboard = GamesListKeyboard(mode="multiplayer").menu_keyboard
        text = "Увы, еще нету созданных игровых комнат, но вы можете создать свою"
    else:
        text = "ID | Тип игры | Ник создателя комнаты"
        games_ids = []
        for game in games_list:
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
            owner = await get_users(telegram_id=game['owner_telegram_id'])
            text += f"\n{game['id']} | {game_type} | {owner['name']}"
            games_ids.append(game['id'])
        text += "\nВы можете зайти в комнату нажав на кнопку с ID этой комнаты"
        if offset == 0:
            back_step = False
        else:
            back_step = True
        next_step_games_list = await get_games(all_games=True, offset=offset+5)
        if len(next_step_games_list) == 0:
            next_step = False
        else:
            next_step = True
        keyboard = GamesListKeyboard(mode="multiplayer", games_ids=games_ids, current_offset=offset, next_step=next_step, back_step=back_step).menu_keyboard
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith("multiplayer_step_offset"))
async def multiplayer_pagination(callback: CallbackQuery):
    await callback.message.delete()
    await game_mode_multiplayer_start(callback.message, offset=int(callback.data.replace("multiplayer_step_offset_", "")))


@dp.callback_query_handler(text="multiplayer_create_game")
async def multiplayer_create_set_game(callback: CallbackQuery):
    await callback.message.delete()
    count_created_games = await get_games(count_created_games=True, telegram_id=callback.from_user.id)
    if count_created_games['count'] >= 5:
        await callback.message.answer("Вы уже создали максимальное количество игровых комнат, ожидайте их завершения", reply_markup=cancel_keyboard(text="Вернуться обратно", callback_data="cancel_multiplayer_create_game"))
        return
    keyboard = GamesListKeyboard(mode="multiplayer", cancel_callback_data="cancel_multiplayer_create_game").keyboard
    await callback.message.answer("Выберите тип игры", reply_markup=keyboard)


@dp.callback_query_handler(text="cancel_multiplayer_create_game")
async def multiplayer_cancel_create_game(callback: CallbackQuery):
    await callback.message.delete()
    await game_mode_multiplayer_start(callback.message)


@dp.callback_query_handler(lambda callback: callback.data.startswith('multiplayer_game'))
async def multiplayer_create_game(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        return
    await create_game(callback.data.replace("multiplayer_game_", ""), callback.from_user.id)
    await callback.message.answer("Игра успешно создана")
    await game_mode_multiplayer_start(callback.message)
    

@dp.callback_query_handler(lambda callback: callback.data.startswith('multiplayer_join'))
async def join_in_game(callback: CallbackQuery, state: FSMContext, game_room_id=None, user_id=None):
    await MultiplayerGameState.in_game.set()
    if game_room_id:
        game = await get_games(game_id=game_room_id)
    else:
        game = await get_games(game_id=int(callback.data.replace("multiplayer_join_", "")))
    async with state.proxy() as data:
        data['in_game'] = True
        data['players'] = [callback.from_user.id, game['owner_telegram_id']]
        data['game_type'] = game['game_type']
        data['game_id'] = game['id']
    if user_id == game['owner_telegram_id'] or game['owner_telegram_id'] == callback.from_user.id:
        await callback.answer("Вы не можете зайти в свою же комнату")
        await state.finish()
        return
    owner_state = dp.current_state(chat=game['owner_telegram_id'], user=game['owner_telegram_id'])
    async with owner_state.proxy() as data:
        try:
            if data['in_game'] == True:
                await callback.answer("Этот пользователь уже в игре, подождите")
                await state.finish()
                return
        except:
            try:
                await callback.message.delete()
            except:
                pass
            data['game_id'] = game['id']
            data['game_type'] = game['game_type']
            data['in_game'] = True
            data['players'] = [callback.from_user.id, game['owner_telegram_id']]
        keyboard = GamesListKeyboard(mode="multiplayer", cancel_text="Выйти из комнаты", cancel_callback_data="cancel_multiplayer_join_game").start_game_keyboard
        if game_room_id:
            msg = await callback.answer("Нажмите \"Начать игру\" в течение 30 секунд иначе игра будет отменена", reply_markup=keyboard)
        else:
            msg = await callback.message.answer("Нажмите \"Начать игру\" в течение 30 секунд иначе игра будет отменена", reply_markup=keyboard)
        msg2 = await bot.send_message(game['owner_telegram_id'], "Нажмите \"Начать игру\" в течение 30 секунд иначе игра будет отменена", reply_markup=keyboard)
        data['msgs'] = [msg, msg2]
        first_player = data['players'][randint(0, 1)]
        data['first_player'] = first_player
    await owner_state.set_state(MultiplayerGameState.in_game)
    await state.update_data({'msgs': [msg, msg2], 'first_player': first_player})
    for i in range(3):
        await sleep(10)
        if await state.get_state() != "MultiplayerGameState.in_game" and await owner_state.get_state() != "MultiplayerGameState.in_game":
            return
    await multiplayer_cancel_join_in_game(callback, state)
        



@dp.callback_query_handler(text="cancel_multiplayer_join_game", state=MultiplayerGameState.in_game)
async def multiplayer_cancel_join_in_game(callback: CallbackQuery, state: FSMContext):
    players = await state.get_data()
    msgs, players = players['msgs'], players['players']
    for player in players:
        current_state = dp.current_state(chat=player, user=player)
        await current_state.finish()
        await bot.send_message(player, "Игра отменена", reply_markup=cancel_keyboard(text="Вернуться обратно", callback_data="cancel_multiplayer_create_game"))
    for msg in msgs:
        await msg.delete()


@dp.callback_query_handler(text="multiplayer_start_game", state=MultiplayerGameState.in_game)
async def multiplayer_ready_to_game(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MultiplayerGameState.game_ready.set()
    players = await state.get_data()
    first_player, game_type, game_id, players = players['first_player'], players['game_type'], players['game_id'], players['players']
    if players[0] == callback.from_user.id:
        other_player = players[1]
    else:
        other_player = players[0]
    other_player_state = dp.current_state(chat=other_player, user=other_player)
    await state.update_data({'other_player': other_player})
    if await other_player_state.get_state() == "MultiplayerGameState:game_ready":
        await callback.message.answer("Игра начинается")
        await bot.send_message(other_player, "Игра начинается")
        if game_type == "dice":
            emoji = "🎲"
            game_text = ['Бросаю кубик', 'у противника выпало', '']
        elif game_type == "dart":
            emoji = "🎯"
            game_text = ['Бросаю дротик', 'противник попал в', 'линию']
        elif game_type == "bowling":
            emoji = "🎳"
            game_text = ['Бросаю шар', 'противник выбил', 'кегли']
        elif game_type == "basketball":
            emoji = "🏀"
            game_text = ['Бросаю мяч', 4]
        elif game_type == "football":
            emoji = "⚽"
            game_text = ['Пинаю мяч', 3]
        await callback.message.answer(f"Отправьте эмодзи {emoji} (Только этот эмодзи без ковычек и других слов)\nЕсли вы не отправите эмодци в течение 30 секунд, то бот сделает за вас это автоматически")
        await bot.send_message(other_player, f"Отправьте эмодзи {emoji} (Только этот эмодзи без ковычек и других слов)\nЕсли вы не отправите эмодци в течение 30 секунд, то бот сделает за вас это автоматически")
        await other_player_state.update_data({'emoji': emoji})
        await state.update_data({'emoji': emoji})
        for i in range(3):
            await sleep(10)
            player_name_state = await state.get_state()
            other_player_name_state = await other_player_state.get_state()
            if other_player_name_state == "MultiplayerGameState:value" and player_name_state == "MultiplayerGameState:value":
                break
            elif i == 2:
                if player_name_state != "MultiplayerGameState:value":
                    await state.set_state(MultiplayerGameState.value)
                    await callback.message.answer(f"{game_text[0]} за вас")
                    msg = await callback.message.answer_dice(emoji=emoji)
                    await state.update_data({'value': msg.dice.value})
                if other_player_name_state != "MultiplayerGameState:value":
                    await other_player_state.set_state(MultiplayerGameState.value)
                    await bot.send_message(other_player, f"{game_text[0]} за вас")
                    msg = await bot.send_dice(other_player, emoji=emoji)
                    await other_player_state.update_data({'value': msg.dice.value})
        other_player_data = await other_player_state.get_data()
        other_player_value = other_player_data['value']
        player_data = await state.get_data()
        player_value = player_data['value']
        if game_type in ['dice', 'dart', 'bowling']:
            if game_type == "dart":
                player_value -= 1
                other_player_value -= 1
            elif game_type == "bowling":
                if player_value <= 2:
                    player_value -= 1
                if other_player_value <= 2:
                    player_value -= 1
            if other_player_value > player_value:
                await callback.message.answer(f"Вы проиграли, {game_text[1]} {other_player_value} {game_text[2]}")
                await bot.send_message(other_player, f"Вы победили, {game_text[1]} {player_value} {game_text[2]}")
                await update_game(game_id, winner=other_player, players=[other_player, callback.from_user.id], status=True)
                await update_user(callback.from_user.id, losses=True)
                await update_user(other_player, wins=True)
                
            elif other_player_value < player_value:
                await callback.message.answer(f"Вы победили, {game_text[1]} {other_player_value} {game_text[2]}")
                await bot.send_message(other_player, f"Вы проиграли, {game_text[1]} {player_value} {game_text[2]}")
                await update_game(game_id, winner=callback.from_user.id, players=[other_player, callback.from_user.id], status=True)
                await update_user(other_player, losses=True)
                await update_user(callback.from_user.id, wins=True)
            else:
                await callback.message.answer("У вас ничья")
                await bot.send_message(other_player, "У вас ничья")
                await update_game(game_id, winner=None, players=[other_player, callback.from_user.id], status=True)
        elif game_type in ["basketball", 'football']:
            if other_player_value >= game_text[1] and player_value < game_text[1]:
                await callback.message.answer(f"Вы проиграли, ваш соперник забил")
                await bot.send_message(other_player, f"Вы победили, ваш соперник не забил")
                await update_user(callback.from_user.id, losses=True)
                await update_user(other_player, wins=True)
                await update_game(game_id, winner=other_player, players=[other_player, callback.from_user.id], status=True)
            elif other_player_value < game_text[1] and player_value >= game_text[1]:
                await callback.message.answer(f"Вы победили, ваш соперник не забил")
                await bot.send_message(other_player, f"Вы проиграли, ваш соперник забил")
                await update_game(game_id, winner=callback.from_user.id, players=[other_player, callback.from_user.id], status=True)
                await update_user(other_player, losses=True)
                await update_user(callback.from_user.id, wins=True)
            else:
                await callback.message.answer("У вас ничья")
                await bot.send_message(other_player, "У вас ничья")
                await update_game(game_id, winner=None, players=[other_player, callback.from_user.id], status=True)
        await state.finish()
        await other_player_state.finish()
    else:
        await callback.message.answer("Ожидаем подтверждение от соперника")


@dp.message_handler(content_types=['dice'], state=MultiplayerGameState.game_ready)
async def multiplayer_get_value(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['emoji'] != message.dice.emoji:
        await message.answer(f"Вы отправили не тот эмодзи, вам нужно отправить {data['emoji']}")
        return
    await MultiplayerGameState.value.set()
    await state.update_data({'value': message.dice.value})
    other_player = data['other_player']
    other_player_state = dp.current_state(chat=other_player, user=other_player)
    if await other_player_state.get_state() != "MultiplayerGameState:value":
        await message.answer("Ожидаем ход противника")