from .users import UserMiddleware


def setup_middlewares(dp):
    dp.setup_middleware(UserMiddleware())