import io
import sys
import aiohttp
import discord
import asyncio
import traceback
from PIL import Image
from bot.extras.emojis import *
from airdrive.errors import FileNotFound
from extslash.commands import ApplicationContext, Bot
from bot.extras.func import db_push_object, db_fetch_object, db_fetch_prefix, drive


class Option(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
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


async def sub_view_welcomecard(ctx: ApplicationContext, bot: Bot):
    reception = await db_fetch_object(guild_id=ctx.guild.id, key='welcome')
    if reception and reception[0].isdigit():
        view = Option(ctx)
        try:
            chunks = drive.cache(f'covers/{ctx.guild.id}_card.png')
        except FileNotFound:
            chunks = drive.cache('covers/default_card.png')
        emd = discord.Embed(description=f'**`current`**')
        emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)
        file = discord.File(io.BytesIO(chunks), filename='default_card.png')
        emd.set_image(url=f'attachment://default_card.png')
        await ctx.edit_response(embed=emd, view=view, file=file)

        await view.wait()

        if view.value == 1:

            def check(m):
                return m.author == ctx.author

            await ctx.send_followup(
                embed=discord.Embed(
                    description=f'> {Emo.IMG} Send the **IMAGE** or **URL** for Welcome Card *(min: 700x300)*'),
                view=None)
            try:
                reply = await bot.wait_for('message', timeout=120, check=check)
                try:
                    path = f'covers/{ctx.guild.id}_card.png'
                    if reply.attachments:
                        chunks = await reply.attachments[0].read()
                        Image.open(io.BytesIO(chunks))
                        emd = discord.Embed(description=f"{Emo.CHECK}  Welcome card accepted")
                        emd.set_image(url='attachment://welcome_card.png')
                        await ctx.send_followup(
                            embed=emd,
                            file=discord.File(io.BytesIO(chunks), filename='welcome_card.png'))
                        drive.upload(remote_file_name=path, file_content=chunks)
                    else:
                        async with aiohttp.ClientSession() as session:
                            resp = await session.get(reply.content)
                            file = await resp.read()
                            Image.open(io.BytesIO(file))
                            await db_push_object(guild_id=ctx.guild.id, item=[reply.content], key='cover')
                            emd = discord.Embed(description=f"{Emo.CHECK}  Welcome card accepted")
                            emd.set_image(url='attachment://welcome_card.png')
                            await ctx.send_followup(
                                embed=emd, file=discord.File(io.BytesIO(file), filename='welcome_card.png'))
                            drive.upload(remote_file_name=path, file_content=file)
                except Exception:
                    await ctx.send_followup(
                        embed=discord.Embed(description=f"{Emo.WARN} This File/URL is not acceptable!"))
            except asyncio.TimeoutError:
                await ctx.send_followup(embed=discord.Embed(description='Bye! you took so long...'))
        elif view.value == 2:
            await ctx.send_followup(embed=discord.Embed(description=f'{Emo.DEL} Welcomecard removed'))
            await db_push_object(guild_id=ctx.guild.id, item=['REMOVED'], key='cover')
            try:
                drive.delete(f'covers/{ctx.guild.id}_card.png')
            except Exception:
                pass
        elif view.value == 0:
            await ctx.delete_response()
    else:
        prefix = await db_fetch_prefix(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel'
                        f'\nfor receiving Welcome Cards'
                        f'\n\n**`Steps`**'
                        f'\n> **/setup**  select **Reception** from menu'
                        f'\n> Then tap **Edit**  select a **text channel** from menu')
        await ctx.edit_response(embed=emd)
