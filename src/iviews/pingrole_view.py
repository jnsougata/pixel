import asyncio
import discord
from src.extras.emojis import *
from extslash.commands import ApplicationContext, Bot
from src.extras.func import db_fetch_object, db_push_object


class Option(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
        self.ctx = ctx
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


async def sub_view_pingrole(ctx: ApplicationContext, bot: Bot):

    data = await db_fetch_object(guild_id=ctx.guild.id, key='arole')
    if data and data[0].isdigit():
        role = ctx.guild.get_role(int(data[0]))
    else:
        role = None

    if role and role == ctx.guild.default_role:
        string = role
    elif role:
        string = role.mention
    else:
        string = '**None**'

    emd = discord.Embed(
        description=f''
                    f'Current **ping role** is {string}'
                    f'\n\n> To set **new** ping role tap **`Edit`**'
                    f'\n\n> This will be used to ping members with youtube notifications'
    )
    emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)

    view = Option(ctx)
    await ctx.edit_response(embed=emd, view=view)
    await view.wait()

    if view.value == 1:
        await ctx.edit_response(
            embed=discord.Embed(description=f'{Emo.INFO} You can now set `@everyone` as ping role'
                                            f'\n\n> {Emo.BELL} Please mention a **role** to set as **Ping Role:**'),
            view=None)

        def check(m):
            return m.author == ctx.author

        try:
            resp = await bot.wait_for('message', check=check, timeout=120)

            if '@everyone' in resp.content:
                role = ctx.guild.default_role
                mention_string = role
            else:
                mentions = resp.role_mentions
                role = mentions[0] if mentions else None
                mention_string = role.mention if role else '**None**'

            if role:
                await ctx.edit_response(
                    embed=discord.Embed(
                        title=f'{Emo.CHECK} Reworked',
                        description=f'Current ping role is {mention_string}'
                                    f'\nThis will be used to ping members with youtube notifications'))
                await db_push_object(guild_id=ctx.guild.id, item=[str(role.id)], key='arole')
            else:
                await ctx.edit_response(embed=discord.Embed(description=f'{Emo.WARN} you did not mention a role'))
        except asyncio.TimeoutError:
            await ctx.send_message('Bye! you took so long')
    elif view.value == 2:
        await ctx.edit_response(
            embed=discord.Embed(
                description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** ping role has been removed')
        )
        await db_push_object(guild_id=ctx.guild.id, item=['REMOVED'], key='arole')

    elif view.value == 0:
        await ctx.delete_response()
