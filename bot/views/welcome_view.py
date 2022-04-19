import discord
import asyncio
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import drive


async def sub_view_welcomecard(bot: Bot, ctx: Context, url: str):
    reception = bot.cached[ctx.guild.id].get('RECEPTION')
    if reception and reception.isdigit():
        emd = discord.Embed(
            title=f'{Emo.CHECK} Welcome Card Updated',
            description=f'Bound to <#{reception}>',
        )
        emd.set_image(url=url)
        await ctx.edit_response(embed=emd)

        def func():
            drive.upload_from_url(url, f'covers/{ctx.guild.id}_card.png')
        bot.loop.run_in_executor(None, func)

    else:
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel'
                        f'\nfor receiving Welcome Cards'
                        f'\n\n**`Steps`**'
                        f'\n> **/setup**  select **reception** from options')
        await ctx.edit_response(embed=emd)
