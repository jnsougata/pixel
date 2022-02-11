import os
from deta import Deta
from typing import Union
from airdrive import AirDrive
from discord.ext import commands


DEFAULT_PREFIX = '.'
KEY = os.getenv('DETA_TOKEN')
deta = Deta(KEY)
drive = AirDrive.login('PixeL', '@11223344', private_key=KEY, silent=True)


async def db_push_object(guild_id: int, item: Union[list, dict, str, int, float], key: str):
    db = deta.Base(f'GUILD{guild_id}')
    return db.put({'item': item}, key)


async def db_fetch_object(guild_id: int, key: str):
    db = deta.Base(f'GUILD{guild_id}')
    data = db.get(key)
    if data:
        return data.get('item')
    return None


async def db_fetch_prefix(guild_id):
    prefix = await db_fetch_object(guild_id=guild_id, key='prefix')
    return prefix[0] if prefix else DEFAULT_PREFIX

