import io
import sys
import aiohttp
import discord
import asyncio
import traceback
from PIL import Image
from airdrive import AirDrive
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_push_object, db_fetch_object, prefix_fetcher, drive


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx
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


async def sub_view_welcomecard(bot: discord.Client, ctx: commands.Context, interaction: discord.Interaction):
    reception = await db_fetch_object(guild_id=ctx.guild.id, key='welcome')
    if reception and reception[0].isdigit():
        view = Option(ctx)
        try:
            _bytes = drive.cache(f'covers/{ctx.guild.id}_card.png')
        except FileNotFoundError:
            _bytes = drive.cache('covers/default_card.png')
        emd = discord.Embed(description=f'**`current`**')
        emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)
        file = discord.File(io.BytesIO(_bytes), filename='default_card.png')
        emd.set_image(url=f'attachment://default_card.png')
        await interaction.response.defer()
        await interaction.message.delete()
        msg = await ctx.send(embed=emd, view=view, file=file)

        await view.wait()

        if view.value == 1:

            def check(m):
                return m.author == ctx.author

            await msg.delete()
            new = await ctx.send(
                embed=discord.Embed(description='Send the Image or URL you want to use as a cover *(min: 700x300)*')
            )
            try:
                reply = await bot.wait_for('message', timeout=20, check=check)
                try:
                    path = f'covers/{ctx.guild.id}_card.png'
                    if reply.attachments:
                        _bytes = await reply.attachments[0].read()
                        Image.open(io.BytesIO(_bytes))
                        emd = discord.Embed(description=f"{Emo.CHECK}  Welcome card accepted")
                        emd.set_image(url='attachment://welcome_card.png')
                        await new.delete()
                        await ctx.send(
                            embed=emd,
                            file=discord.File(io.BytesIO(_bytes), filename='welcome_card.png')
                        )
                        drive.upload(remote_file_name=path, file_content=_bytes)
                    else:
                        async with aiohttp.ClientSession() as session:
                            resp = await session.get(reply.content)
                            file = await resp.read()
                            Image.open(io.BytesIO(file))
                            await db_push_object(guild_id=ctx.guild.id, item=[reply.content], key='cover')
                            emd = discord.Embed(description=f"{Emo.CHECK}  Welcome card accepted")
                            emd.set_image(url='attachment://welcome_card.png')
                            await new.delete()
                            await ctx.send(
                                embed=emd,
                                file=discord.File(io.BytesIO(file), filename='welcome_card.png')
                            )
                            drive.upload(remote_file_name=path, file_content=file)
                except Exception as e:
                    print(e)
                    await ctx.send(
                        embed=discord.Embed(description=f"{Emo.WARN} This File/URL is not acceptable!")
                    )
            except asyncio.TimeoutError:
                await new.edit(embed=discord.Embed(description='Bye! you took so long...'))
        elif view.value == 2:
            await ctx.send(embed=discord.Embed(description=f'{Emo.DEL} Welcomecard removed'), delete_after=5)
            await db_push_object(guild_id=ctx.guild.id, item=['REMOVED'], key='cover')
        elif view.value == 0:
            await msg.delete()
        else:
            pass
    else:
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel '
                        f'\nfor receiving Welcome Cards'
                        f'\n\n**`Steps`**'
                        f'\n**{prefix}setup**  select **reception** from menu'
                        f'\nThen tap **Edit**  select a **text channel** from menu'
        )
        await ctx.send(embed=emd)
