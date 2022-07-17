from asyncpg import connect
from data import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_DSN


async def get_conn():
    conn = await connect(dsn=DB_DSN, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    return conn