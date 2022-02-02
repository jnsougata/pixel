import asyncio
import discord
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_fetch_prefix, db_push_object


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.message = None
        super().__init__()
        self.value = None

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


async def sub_view_prefix(
        bot: discord.Client,
        ctx: commands.Context,
        interaction: discord.Interaction,
):
    prefix = await db_fetch_prefix(ctx.guild.id)
    emd = discord.Embed(
        description=f'**{ctx.guild.me.display_name}\'s** current prefix is **` {prefix} `**'
                    f'\n\nTo set new custom prefix tap **` Edit `**'
    )
    if ctx.guild.icon:
        emd.set_author(icon_url=ctx.guild.icon.url, name=ctx.guild.name)
    else:
        emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)

    view = Option(ctx)
    await interaction.response.defer()
    await interaction.message.delete()
    msg = await ctx.send(embed=emd, view=view)

    await view.wait()

    if view.value == 1:
        new = await msg.edit(
            embed=discord.Embed(description='Please **type** a prefix to set as **custom prefix:**'),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=120)
            if 0 < len(response.content) <= 3:
                await db_push_object(guild_id=ctx.guild.id, item=[response.content], key='prefix')
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                                    f'new custom prefix is  ` {response.content} `')
                )
            else:
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} Please try again with **3** or **less** characters!')
                )
        except asyncio.TimeoutError:
            await ctx.send('Bye! you took so long...')
    elif view.value == 2:
        await msg.edit(embed=discord.Embed(description=f'{Emo.DEL} Custom prefix removed'), view=None)
        await db_push_object(guild_id=ctx.guild.id, item=['.'], key='prefix')
    elif view.value == 0:
        await msg.delete()
