from .conn import get_conn


async def get_users(telegram_id=False, count=False):
    conn = await get_conn()
    if telegram_id:
        res = await conn.fetchrow('SELECT * FROM users1 WHERE telegram_id = $1', telegram_id)
    elif count:
        res = await conn.fetchrow('SELECT COUNT(*) FROM users1')
    await conn.close()
    return res


async def get_games(all_games=False, user_games=False, game_id=False, count=False, count_created_games=False, telegram_id=None, offset=0):
    conn = await get_conn()
    if all_games:
        res = await conn.fetch('SELECT * FROM games WHERE status = false ORDER BY id LIMIT 5 OFFSET $1', offset)
    elif game_id:
        res = await conn.fetchrow('SELECT * FROM games WHERE id = $1', game_id)
    elif count:
        res = await conn.fetchrow(f'SELECT COUNT(*) FROM games WHERE {telegram_id}=ANY(players)')
    elif user_games:
        res = await conn.fetch(f'SELECT * FROM games WHERE {telegram_id}=ANY(players) AND status=true ORDER BY id LIMIT 5 offset {offset}')
    elif count_created_games:
        res = await conn.fetchrow(f'SELECT COUNT(*) FROM games WHERE {telegram_id}=ANY(players) AND status = false')
    await conn.close()
    return res