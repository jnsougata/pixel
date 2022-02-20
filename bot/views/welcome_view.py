import aiohttp
import discord
import asyncio
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object, drive


class Option(discord.ui.View):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        super().__init__()
        self.value = None

    @discord.ui.button(label='New', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def remove(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 0
            self.stop()


async def sub_view_welcomecard(ctx: Context, url: str):
    reception = await db_fetch_object(guild_id=ctx.guild.id, key='welcome')
    if reception and reception[0].isdigit():
        emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card Updated')
        emd.set_image(url=url)
        await ctx.edit_response(embed=emd)

        def func():
            drive.upload_from_url(url, f'covers/{ctx.guild.id}_card.png')
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, func)

    else:
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel'
                        f'\nfor receiving Welcome Cards'
                        f'\n\n**`Steps`**'
                        f'\n> **/setup**  select **reception** from options')
        await ctx.edit_response(embed=emd)
