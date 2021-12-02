import io
import discord
import asyncio
import aiohttp
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
        self.value = None
        self.timeout = 30

    async def on_timeout(self) -> None:
        try:
            self.clear_items()
            await self.message.edit(view=self)
        except discord.errors.NotFound:
            return


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.message = None

        super().__init__()
        self.value = None

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def remove(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = None
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
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
    if rcp_raw and rcp_raw['item']:
        raw = await db_fetch_object(
            guildId=ctx.guild.id,
            key='cover'
        )
        emd = discord.Embed(
            description=f'To set new welcome card tap **` Edit `**'
                        f'\n\n**Current Welcome card:**'
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
            card = raw['item'][0]
            emd.set_image(url=card)
        else:
            card = 'https://i.imgur.com/CLy9KUO.jpg'
            emd.set_image(url=card)
            emd.set_footer(text='(Default Image)')
        view = Option(ctx)
        await interaction.response.edit_message(embed=emd, view=view)
        await view.wait()
        if view.value is True:

            def check(m):
                return m.author == ctx.author

            await interaction.message.edit(
                embed=discord.Embed(description='Please paste URL of an Image **700x300(min)**:'),
                view=None
            )
            try:
                reply = await bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                await ctx.send('**Bye! you took so long!**')
                return
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(reply.content) as response:
                        resp = await response.read()
                        Image.open(io.BytesIO(resp))
                        await db_push_object(
                            guildId=ctx.guild.id,
                            item=[reply.content],
                            key='cover'
                        )
                        await ctx.send(
                            embed=discord.Embed(description=f"{Emo.CHECK} **Cover picture accepted**")
                        )
            except Exception as e:
                print(e)
                await ctx.send(
                    embed=discord.Embed(description=f"{Emo.WARN} **URL is not acceptable**")
                )
            pass
        elif view.value is None:
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
        elif view.value is False:
            await interaction.delete_original_message()
    else:
        p = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Reception Found {Emo.WARN}',
            description=f'Please set a Text Channel '
                        f'\nfor receiving Welcome Message Cards'
                        f'\n\n**`Steps`**'
                        f'\n**{p}setup**  select **reception** from menu '
                        f'\nThen tap **Edit**  select **text channel** from menu'
        )
        await interaction.response.edit_message(embed=emd, view=None)
