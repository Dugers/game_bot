from aiogram.dispatcher.filters.state import StatesGroup, State


class UserUpdateProfileState(StatesGroup):
    name = State()

class BotGamesState(StatesGroup):
    user_value = State()

class MultiplayerGameState(StatesGroup):
    in_game = State()
    game_ready = State()
    value = State()