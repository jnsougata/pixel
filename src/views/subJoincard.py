import io
import sys
import discord
import asyncio
import aiohttp
import traceback
from PIL import Image
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_push_object, db_fetch_object, prefix_fetcher


class BaseView(discord.ui.View):
    def __init__(
            self,
            message: discord.Message = None,
    ):
        self.message = message
        super().__init__()
        self.value = 1
        self.timeout = 30

    async def on_timeout(self) -> None:
        try:
            self.clear_items()
            await self.message.edit(view=self)
        except discord.errors.NotFound:
            return


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx
        self.value = None
        self.message = None

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
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


async def sub_view_welcomecard(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    rcp_raw = await db_fetch_object(
        guildId=ctx.guild.id,
        key='welcome'
    )
    if rcp_raw and rcp_raw['item'] and rcp_raw['item'][0].isdigit():
        raw = await db_fetch_object(
            guildId=ctx.guild.id,
            key='cover'
        )
        emd = discord.Embed(
            description=f'Tap **`Edit`** to set new.'
                        f'\n\nCurrent Image:'
        )
        if ctx.guild.icon:
            emd.set_author(
                icon_url=ctx.guild.icon.url,
                name=ctx.guild.name
            )
        else:
            emd.set_author(
                icon_url=ctx.guild.me.avatar.url,
                name=ctx.guild.me.name
            )
        if raw and raw['item'][0] != 'removed':
            emd.set_image(url=raw['item'][0])
        else:
            emd.set_image(url='https://i.imgur.com/CLy9KUO.jpg')
            emd.set_footer(text='Default Card')
        view = Option(ctx)
        await interaction.response.edit_message(embed=emd, view=view)
        await view.wait()

        if view.value == 1:

            def check(m):
                return m.author == ctx.author

            await interaction.message.edit(
                embed=discord.Embed(description='Paste url of an image min *(700x300)* :'),
                view=None
            )
            try:
                reply = await bot.wait_for('message', timeout=20, check=check)
                try:
                    async with aiohttp.ClientSession() as session:
                        resp = await session.get(reply.content)
                        file = await resp.read()
                        Image.open(io.BytesIO(file))
                        await db_push_object(
                            guildId=ctx.guild.id,
                            item=[reply.content],
                            key='cover'
                        )
                        emd = discord.Embed(description=f"{Emo.CHECK}  Welcome card accepted")
                        emd.set_image(url='attachment://welcome_card.png')
                        await ctx.send(
                            embed=emd,
                            file=discord.File(io.BytesIO(file), filename='welcome_card.png')
                        )
                except Exception:
                    await ctx.send(
                        embed=discord.Embed(description=f"{Emo.WARN} This url is not acceptable")
                    )
            except asyncio.TimeoutError:
                await ctx.send('Bye! you took so long...')
                return
        elif view.value == 2:
            await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description=f'{Emo.DEL} Welcomecard removed'
                ),
                view=None
            )
            await db_push_object(
                guildId=ctx.guild.id,
                item=['removed'],
                key='cover'
            )
        elif view.value == 0:
            await interaction.delete_original_message()
    else:
        p = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel '
                        f'\nfor receiving Welcome Cards'
                        f'\n\n**`Steps`**'
                        f'\n**{p}setup**  select **reception** from menu'
                        f'\nThen tap **Edit**  select a **text channel** from menu'
        )
        await interaction.response.edit_message(embed=emd, view=None)
