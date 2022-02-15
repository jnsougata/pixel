import asyncio
import discord
from bot.extras.emojis import *
from extslash import ApplicationContext, Bot
from bot.extras.func import db_fetch_object, db_push_object


async def sub_view_pingrole(ctx: ApplicationContext, bot: Bot, role: discord.Role):
    if role == ctx.guild.default_role:
        mention = '@everyone'
    else:
        mention = role.mention
    await ctx.edit_response(
        embed=discord.Embed(
            title=f'{Emo.CHECK} Ping Role Updated',
            description=f'Ping role is set to {mention}'
                        f'\nThis will be used to ping members with youtube notifications'))
    await db_push_object(guild_id=ctx.guild.id, item=[str(role.id)], key='arole')
