from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
profile_button = KeyboardButton("Мой профиль")
play_button = KeyboardButton("Играть")
repost_game_button = KeyboardButton("Поделиться")
main_menu_keyboard.add(profile_button, play_button, repost_game_button)