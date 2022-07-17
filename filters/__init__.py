from .users import UserInputFilter


def setup_filters(dp):
    dp.bind_filter(UserInputFilter)