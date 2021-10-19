import os
from deta import Deta
from typing import Union
from discord.ext import commands



deta = Deta(os.getenv('DETA_TOKEN'))
DEFAULT_PREFIX = '.'



async def db_push_object(
    guildId: int, 
    item: Union[list, dict], 
    key: str
):
    db = deta.Base(f'GUILD{guildId}')
    db.put({'item': item}, key)




async def db_fetch_object(
        guildId: int,
        key: str
):
    db = deta.Base(f'GUILD{guildId}')
    return db.get(key)




async def prefix_fetcher(id):

    prefix = await db_fetch_object(guildId=id, key='prefix')
    return prefix['item'][0] if prefix and len(prefix['item']) > 0 else DEFAULT_PREFIX




async def custom_prefix(bot, msg):

    if msg.guild:

        prefixes = await db_fetch_object(guildId = msg.guild.id, key='prefix')

        if prefixes and len(prefixes['item']) > 0:
            return commands.when_mentioned_or(prefixes['item'][0])(bot, msg)

        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)

    else:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, msg)

