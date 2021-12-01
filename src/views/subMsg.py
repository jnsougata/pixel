import asyncio
import discord
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_fetch_object, db_push_object


class Exit(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        super().__init__()
        self.value = None

    @discord.ui.button(label='Exit', style=discord.ButtonStyle.red)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()


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


async def sub_view_alert_msg(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    data: dict = await db_fetch_object(
        guildId=ctx.guild.id,
        key='msg'
    )
    emd = discord.Embed(
        description=f'**{ctx.guild.me.display_name}\'s** current custom alert message:'
                    f'\n\n**` {data["item"] if data else None} `**'
                    f'\n\nTo set new alert message tap **` Edit `**'
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
    view = Option(ctx)
    await interaction.response.edit_message(embed=emd, view=view)
    await view.wait()

    if view.value is True:
        new = await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please **type** a **custom alert message:**'
            ),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=20)
            if data:
                data["item"]["ytmsg"] = response.content
                temp = data['item']
            else:
                temp = {"ytmsg": response.content}
            await db_push_object(
                guildId=ctx.guild.id,
                item=temp,
                key='msg'
            )
            await new.delete()
            await ctx.send(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    title='Coming Soon!',
                    description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                                f'new custom alert message:\n\n` {response.content} `',
                )
            )
        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')

    elif view.value is False:
        try:
            await interaction.delete_original_message()
        except discord.NotFound:
            pass
    else:
        if data and data["item"].get("ytmsg"):
            data["item"].pop("ytmsg")
            await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description=f'{Emo.DEL} Custom alert message removed'
                ),
                view=None
            )
            await db_push_object(
                guildId=ctx.guild.id,
                item=data["item"],
                key='msg'
            )
        else:
            await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description=f'{Emo.WARN} Please add custom alert message'
                ),
                view=None
            )
