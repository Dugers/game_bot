from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


profile_menu_keyboard = InlineKeyboardMarkup()
update_name_button = InlineKeyboardButton(text="Изменить никнейм", callback_data="update_name")
games_history_button = InlineKeyboardButton("История игр", callback_data="games_history")
profile_menu_keyboard.add(update_name_button, games_history_button)

def cancel_keyboard(text, callback_data="cancel", button=False):
    if button:
        return InlineKeyboardButton(text=text, callback_data=callback_data)
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, callback_data=callback_data))

# Games Keyboards 

select_game_keyboard = InlineKeyboardMarkup()
game_mode_bot_button = InlineKeyboardButton("Играть с ботом", callback_data="game_mode_bot")
game_mode_multiplayer_keyboard = InlineKeyboardButton("Играть с другими людьми", callback_data="game_mode_multiplayer")
select_game_keyboard.add(game_mode_bot_button, game_mode_multiplayer_keyboard)


class GamesListKeyboard:
    
    # game modes:
    # bot - game with a bot
    # multiplayer - game with multiple people

    def __init__(self, mode, cancel_text="Вернуться обратно", cancel_callback_data="cancel_games_list", games_ids=None, current_offset=None, next_step=False, back_step=False):
        self.mode = mode
        self.cancel_text = cancel_text
        self.cancel_callback_data = cancel_callback_data
        self.games_ids = games_ids
        self.current_offset = current_offset
        self.next_step = next_step
        self.back_step = back_step
    
    @property
    def keyboard(self):
        list_keyboard = InlineKeyboardMarkup()
        dice_button = InlineKeyboardButton("Бросить кубик", callback_data=f"{self.mode}_game_dice")
        dart_button = InlineKeyboardButton("Играть в дартс", callback_data=f"{self.mode}_game_dart")
        bowling_button = InlineKeyboardButton("Играть в боулинг", callback_data=f"{self.mode}_game_bowling")
        basketball_button = InlineKeyboardButton("Играть в баскетбол", callback_data=f"{self.mode}_game_basketball")
        football_button = InlineKeyboardButton("Играть в футбол", callback_data=f"{self.mode}_game_football")
        cancel_button = cancel_keyboard(text=self.cancel_text, callback_data=self.cancel_callback_data, button=True)
        list_keyboard.row(dice_button, dart_button, bowling_button).row(basketball_button, football_button).row(cancel_button)
        if self.mode == "bot":
            return list_keyboard
        elif self.mode == "multiplayer":
            return list_keyboard
    @property
    def menu_keyboard(self):
        if self.mode == "multiplayer":
            keyboard = InlineKeyboardMarkup(row_width=7)
            if not (self.games_ids is None):
                if self.back_step:
                    keyboard.insert(InlineKeyboardButton(text="<-", callback_data=f"multiplayer_step_offset_{self.current_offset - 5}"))
                for game_id in self.games_ids:
                    keyboard.insert(InlineKeyboardButton(text=str(game_id), callback_data=f"multiplayer_join_{game_id}"))
                if self.next_step:
                    keyboard.insert(InlineKeyboardButton(text="->", callback_data=f"multiplayer_step_offset_{self.current_offset + 5}"))
            create_game_button = InlineKeyboardButton("Создать игровую комнату", callback_data="multiplayer_create_game")
            cancel_button = cancel_keyboard(text=self.cancel_text, callback_data=self.cancel_callback_data, button=True)
            keyboard.row(create_game_button).row(cancel_button)
            return keyboard
        else:
            return False

    @property
    def start_game_keyboard(self):
        if self.mode == "multiplayer":
            keyboard = InlineKeyboardMarkup()
            ready_to_start_game = InlineKeyboardButton("Начать игру", callback_data="multiplayer_start_game")
            cancel_button = cancel_keyboard(text=self.cancel_text, callback_data=self.cancel_callback_data, button=True)
            keyboard.row(ready_to_start_game).row(cancel_button)
            return keyboard
        else:
            return False


def games_history_keyboard(offset=0, next_step=False, back_step=False):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if back_step:
        keyboard.insert(InlineKeyboardButton("<-", callback_data=f"games_history_step_{offset - 5}"))
    if next_step:
        keyboard.insert(InlineKeyboardButton("->", callback_data=f"games_history_step_{offset + 5}"))
    keyboard.row(cancel_keyboard("Вернуться обратно", "cancel_games_history", button=True))
    return keyboard