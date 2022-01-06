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
    all_ = bot.temp_prefixes
    if msg.guild:
        return commands.when_mentioned_or(all_[msg.guild.id])(bot, msg)
    else:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)


async def cache_all_prefix(bot):
    temp = {}
    for guild in bot.guilds:
        prefix = await db_fetch_object(guild_id=guild.id, key='prefix')
        if prefix and prefix['item']:
            temp[guild.id] = prefix['item'][0]
        else:
            temp[guild.id] = DEFAULT_PREFIX

    return temp
