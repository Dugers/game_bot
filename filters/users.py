from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message


class UserInputFilter(BoundFilter):

    # types:
    # name = string and lenght in [3:30] and not have @, /
    # if invalid True filter return reverse answer


    def __init__(self, type, invalid=False):
        self.type = type
        self.invalid = int(invalid)

    async def check(self, message: Message):
        if self.type == "name":
            if message.text.isdigit():
                return [False, True][self.invalid]
            if "/" in message.text or "@" in message.text:
                return [False, True][self.invalid]
            if len(message.text) > 30 or len(message.text) < 3:
                return [False, True][self.invalid]
            return [True, False][self.invalid]