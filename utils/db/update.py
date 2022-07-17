from .conn import get_conn


async def update_user(telegram_id, name=False, wins=False, losses=False):
    conn = await get_conn()
    if name:
        await conn.execute('UPDATE users SET name = $1 WHERE telegram_id = $2', name, telegram_id)
    if wins:
        await conn.execute('UPDATE users SET wins = wins + 1 WHERE telegram_id = $1', telegram_id)
    if losses:
        await conn.execute('UPDATE users SET losses = losses + 1 WHERE telegram_id = $1', telegram_id)
    await conn.close()


async def update_game(game_id, winner=False, players=False, status=False):
    conn = await get_conn()
    if players and status:
        await conn.execute('UPDATE games SET winner = $1, players = $2, status = $3 WHERE id = $4', winner, players, status, game_id)
    await conn.close()
    