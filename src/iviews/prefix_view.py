import asyncio
import discord
from src.extras.emojis import *
from extslash.commands import ApplicationContext, Bot
from src.extras.func import db_fetch_prefix, db_push_object


class Option(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
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


async def sub_view_prefix(ctx: ApplicationContext, bot: Bot):
    prefix = await db_fetch_prefix(ctx.guild.id)
    emd = discord.Embed(
        description=f'Current prefix is **`{prefix}`**'
                    f'\n\n> To set new custom prefix tap **`Edit`**'
                    f'\n\n> {Emo.INFO} You can always mention me and type any command')
    emd.set_author(icon_url=ctx.me.avatar.url, name=ctx.me.name)
    view = Option(ctx)
    await ctx.edit_response(embed=emd, view=view)

    await view.wait()

    if view.value == 1:
        await ctx.edit_response(
            embed=discord.Embed(description=f'{Emo.TAG} Please **type** a prefix to set as **Custom Prefix:**'),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=120)
            if 0 < len(response.content) <= 3:
                await db_push_object(guild_id=ctx.guild.id, item=[response.content], key='prefix')
                await ctx.edit_response(
                    embed=discord.Embed(
                        title=f'{Emo.CHECK} Reworked',
                        description=f'The current set custom prefix is  `{response.content}`'))
            else:
                await edit_response(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} Please try again with **3** or **less** characters!'))
        except asyncio.TimeoutError:
            await ctx.send_message('Bye! you took so long...')
    elif view.value == 2:
        await edit_response(embed=discord.Embed(description=f'{Emo.DEL} Custom prefix removed'), view=None)
        await db_push_object(guild_id=ctx.guild.id, item=['.'], key='prefix')
    elif view.value == 0:
        await ctx.delete_response()
