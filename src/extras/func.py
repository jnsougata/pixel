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


async def db_push_blacklist(item):
    db = deta.Base(f'BLACKLIST')
    db.put({'item': item}, 'list')


async def db_fetch_blacklist():
    db = deta.Base(f'BLACKLIST')
    return db.get('list')


async def prefix_fetcher(id):
    prefix = await db_fetch_object(guild_id=id, key='prefix')
    return prefix['item'][0] if prefix and len(prefix['item']) > 0 else DEFAULT_PREFIX


async def custom_prefix(bot, msg):
    if msg.guild:
        prefixes = await db_fetch_object(guild_id=msg.guild.id, key='prefix')
        if prefixes and prefixes['item']:
            return commands.when_mentioned_or(prefixes['item'][0])(bot, msg)
        else:
            return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)
    else:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)
