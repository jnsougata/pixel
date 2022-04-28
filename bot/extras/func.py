import os
from deta import Deta
from typing import Union
from airdrive import AirDrive
from discord.ext import commands

deta = Deta(os.getenv('DETA_TOKEN'))


async def db_push_object(guild_id: int, item: Union[list, dict, str, int, float], key: str):
    db = deta.Base(f'GUILD{guild_id}')
    return db.put({'item': item}, key)


async def db_fetch_object(guild_id: int, key: str):
    db = deta.Base(f'GUILD{guild_id}')
    data = db.get(key)
    if data:
        return data.get('item')
    return None
