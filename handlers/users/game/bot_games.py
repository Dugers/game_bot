from loader import dp
from states import BotGamesState
from asyncio import sleep
from keyboards.inline import GamesListKeyboard
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery


async def game_mode_bot_start(message: Message):
    games_list = GamesListKeyboard(mode="bot").keyboard
    await message.answer("Выберите игру", reply_markup=games_list)


@dp.callback_query_handler(lambda callback: callback.data.startswith('bot_game_'))
async def bot_send_in_game(callback: CallbackQuery, state):
    await callback.message.delete()
    game = callback.data.replace("bot_game_", "")
    await BotGamesState.user_value.set()
    if game == "dice":
        await bot_game(callback.message, state, emoji="🎲", text=['бросаю кубик', 'бросить кубик', 'кубик который я кинул'])
        return
    elif game == "dart":
        await bot_game(callback.message, state, emoji="🎯", text=['кидаю дротик', 'кинуть дротик', 'доску дартса которую я отправил'])
        return
    elif game == "basketball":
        await bot_game(callback.message, state, emoji="🏀", text=['кидаю мяч', 'кинуть мяч', 'баскетбольное кольцо которое я отправил'])
        return
    elif game == "football":
        await bot_game(callback.message, state, emoji="⚽", text=['пинаю мяч', 'пнуть мяч', 'ворота которые я отправил'])
        return
    elif game == "bowling":
        await bot_game(callback.message, state, emoji="🎳", text=['кидаю мяч', 'кинуть мяч', 'кегли которые остались'])


async def bot_game(message: Message, state: FSMContext, emoji, text):
    await message.answer(f"Я {text[0]} первым")
    await message.answer(f"Ваша задача {text[1]} отправив эмодзи {emoji} (Только этот эмодзи без ковычек и других слов) или кликнуть на {text[2]} и нажать \"Отправить\"")
    msg = await message.answer_dice(emoji=emoji)
    async with state.proxy() as data:
        data['bot_value'] = msg.dice.value
        data['game'] = emoji


@dp.message_handler(content_types=['dice'], state=BotGamesState.user_value)
async def bot_game_result(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if data['game'] != message.dice.emoji:
            await message.answer("Упс... Вы отправили не тот эмодзи, отправьте мне такой же который отправил я")
            return
        game = data['game']
        bot_value = data['bot_value']
    await state.finish()
    await sleep(4)
    if game in ['🎲', '🎯', '🎳']:
        if message.dice.value > bot_value:
            await message.answer("Вы победили")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTFi0WAWEry1MfIVRsGO5Aq_857xiAACjhUAAiVNwUmPFk1-69E28ykE")
        elif message.dice.value < bot_value:
            await message.answer("К сожалению вы проиграли")
            await message.answer_sticker("CAACAgIAAxkBAAEFSS9i0V_XfwicSsGYYDOI3Pqj3xNmFAACfhoAAoJV2El4Aq6LUB44mykE")
        else:
            await message.answer("У нас ничья")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTNi0WBD5D2tr0_J67irRxDK3Iv1mwACdBkAAv3EyUkrrD3DFv2fpSkE")
    elif game == "🏀":
        if message.dice.value >= 4 and bot_value < 4:
            await message.answer("Вы победили")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTFi0WAWEry1MfIVRsGO5Aq_857xiAACjhUAAiVNwUmPFk1-69E28ykE")
        elif message.dice.value < 4 and bot_value >= 4:
            await message.answer("Вы проиграли")
            await message.answer_sticker("CAACAgIAAxkBAAEFSS9i0V_XfwicSsGYYDOI3Pqj3xNmFAACfhoAAoJV2El4Aq6LUB44mykE")
        else:
            await message.answer("У нас ничья")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTNi0WBD5D2tr0_J67irRxDK3Iv1mwACdBkAAv3EyUkrrD3DFv2fpSkE")
    elif game == "⚽":
        if message.dice.value >= 3 and bot_value < 3:
            await message.answer("Вы победили")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTFi0WAWEry1MfIVRsGO5Aq_857xiAACjhUAAiVNwUmPFk1-69E28ykE")
        elif message.dice.value < 3 and bot_value >= 3:
            await message.answer("Вы проиграли")
            await message.answer_sticker("CAACAgIAAxkBAAEFSS9i0V_XfwicSsGYYDOI3Pqj3xNmFAACfhoAAoJV2El4Aq6LUB44mykE")
        else:
            await message.answer("У нас ничья")
            await message.answer_sticker("CAACAgIAAxkBAAEFSTNi0WBD5D2tr0_J67irRxDK3Iv1mwACdBkAAv3EyUkrrD3DFv2fpSkE")
    
    await game_mode_bot_start(message)