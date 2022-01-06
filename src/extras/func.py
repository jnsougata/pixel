import os
from deta import Deta
from typing import Union
from discord.ext import commands


deta = Deta(os.getenv('DETA_TOKEN'))
DEFAULT_PREFIX = '.'


async def db_push_object(
    guild_id: int,
    item: Union[list, dict], 
    key: str
):
    db = deta.Base(f'GUILD{guild_id}')
    db.put({'item': item}, key)


async def db_fetch_object(
        guild_id: int,
        key: str
):
    db = deta.Base(f'GUILD{guild_id}')
    return db.get(key)


async def prefix_fetcher(id):
    prefix = await db_fetch_object(guild_id=id, key='prefix')
    return prefix['item'][0] if prefix and prefix['item'] else DEFAULT_PREFIX


async def exec_prefix(bot, msg):
    if msg.guild:
        data = await db_fetch_object(guild_id=msg.guild.id, key='prefix')
        if data and data['item']:
            return commands.when_mentioned_or(data['item'][0])(bot, msg)
        else:
            return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)
    else:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)
