import discord
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object


async def sub_view_receiver(ctx: Context, channel: discord.TextChannel):
    emd = discord.Embed(
        title=f'{Emo.CHECK} Receiver Updated',
        description=f'The current set default receiver channel is {channel.mention}'
                    f'\nThis channel will be used to receive livestream & upload notifications')
    await ctx.edit_response(embed=emd)
    await db_push_object(guild_id=ctx.guild.id, item=[str(channel.id)], key='alertchannel')
