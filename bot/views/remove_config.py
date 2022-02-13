import io
import aiotube
import discord
import asyncio
from bot.extras.emojis import Emo
from extslash.commands import ApplicationContext, Bot
from bot.extras.func import db_fetch_object, drive, db_push_object


async def sub_view_config(value: int, ctx: ApplicationContext, bot: Bot):


    if value == 0:
        data = await db_fetch_object(ctx.guild.id, 'receivers')
        if data:
            await ctx.send_followup(embed=discord.Embed(description='> Please select a channel from menu below:'))
        else:
            await ctx.send_followup(embed=discord.Embed(description='> There is no channel to remove.'))
