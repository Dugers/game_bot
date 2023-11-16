from .conn import get_conn


async def create_tables():
    conn = await get_conn()
    await create_table_users(conn)
    await create_table_games(conn)
    await conn.close()


async def create_table_users(conn):
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS users1 (
        id serial PRIMARY KEY,
        telegram_id bigint,
        name text,
        wins integer DEFAULT 0,
        losses integer DEFAULT 0
    )
    ''')


async def create_table_games(conn):
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id serial PRIMARY KEY,
        game_type text,
        owner_telegram_id bigint,
        players bigint[],
        winner bigint,
        status boolean DEFAULT false
    )
    ''')


async def create_user(telegram_id, name):
    conn = await get_conn()
    await conn.execute('INSERT INTO users1(telegram_id, name) VALUES($1, $2)', telegram_id, name)
    await conn.close()


async def create_game(game_type, owner_telegram_id):
    conn = await get_conn()
    await conn.execute('INSERT INTO games(game_type, owner_telegram_id) VALUES($1, $2)', game_type, owner_telegram_id)
    await conn.close()