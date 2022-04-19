import asyncio
import discord
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_fetch_object, db_push_object


async def sub_view_pingrole(bot: Bot, ctx: Context, role: discord.Role):
    if role == ctx.guild.default_role:
        mention = '@everyone'
    else:
        mention = role.mention
    await ctx.edit_response(
        embed=discord.Embed(
            title=f'{Emo.CHECK} Ping Role Updated',
            description=f'Ping role is set to {mention}'
                        f'\nThis will be used to ping members with youtube notifications'))

    bot.cached[ctx.guild.id]['PINGROLE'] = str(role.id)
    await bot.db.add_field(key=str(ctx.guild.id), field=Field('PINGROLE', str(role.id)), force=True)

