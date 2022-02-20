import discord
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object


async def sub_view_reception(ctx: Context, channel: discord.TextChannel):
    emd = discord.Embed(
        title=f'{Emo.CHECK} Reception Updated',
        description=f'Current set reception channel is {channel.mention}'
                    f'\nThis channel will be used to send welcome cards')
    await ctx.edit_response(embed=emd)
    await db_push_object(guild_id=ctx.guild.id, item=[str(channel.id)], key='welcome')
