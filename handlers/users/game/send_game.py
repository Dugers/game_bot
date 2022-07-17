from hashlib import md5
from loader import dp, bot
from data import BOT_USERNAME
from utils.db import get_games, get_users
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message
from aiogram.utils.markdown import hlink


@dp.message_handler(lambda message: message.text.lower() == "поделиться")
async def sned_game_information(message: Message):
    await message.answer(f"Для того что-бы поделиться игрой с другим пользователем вам нужно:\nЗайдите в диалог к тому кого хотите пригласить\nОбратитесь к боту написав @{BOT_USERNAME}\nЗатем начните вводить ID комнаты\nКогда закончите посмотрите результат\nЕсли результат будет содержать ваш ID комнаты, то нажмите на него и автоматически будет создана ссылка для вступления в комнату\nПример результата:")
    await message.answer_photo("https://i.ibb.co/tQ8XvmF/photo-2022-07-17-15-29-52.jpg")
    await message.answer_photo("https://i.ibb.co/XF4NqH4/photo-2022-07-17-15-33-45.jpg")


@dp.inline_handler()
async def send_game(query: InlineQuery):
    text = query.query or 'ops'
    try:
        game = await get_games(game_id=int(text))
        if game is None:
            raise TypeError
        if game['status'] == True:
            raise ValueError
        owner_game = await get_users(telegram_id=game['owner_telegram_id'])
        type_game = game['game_type'].replace("dice", "Кости").replace("dart", "Дартс").replace("bowling", "Боулинг").replace("basketball", "Баскетбол").replace("football", "Футбол")
        title_text = f"Игровая комната с ID: {text}"
        sending_text = f"Игровая комната с ID: <b>{text}</b>"
        sending_text += f"\nСоздатель комнаты: <b>{owner_game['name']}</b>"
        sending_text += f"\nТип игры : <b>{type_game}</b>"
        sending_text += f"\n<b>{hlink('Вступить в игру', f'https://t.me/testbotlearn_bot?start=join_{text}')}</b>"
    except:
        title_text = "Такой игры не существует"
        sending_text = "Такой игры не существует"
        try:
            if game['status'] == True:
                title_text = "Игра уже завершена"
                sending_text = "Игра уже завершена"
        except:
            pass
    input_content = InputTextMessageContent(sending_text)
    result_id: str = md5(text.encode()).hexdigest()
    item = InlineQueryResultArticle(
        id=result_id,
        title=title_text,
        input_message_content=input_content,
    )
    await bot.answer_inline_query(query.id, results=[item], cache_time=3)