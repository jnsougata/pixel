import asyncio
import discord
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_fetch_object, db_push_object


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


async def sub_view_rping(
        bot: discord.Client,
        ctx: commands.Context,
        interaction: discord.Interaction,
):
    await interaction.response.defer()
    await interaction.message.delete()
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
        description=f'**{ctx.guild.name}\'s** current **ping role** is {string}'
                    f'\n\nTo set new **ping role** tap **` Edit `**'
    )
    if ctx.guild.icon:
        emd.set_author(icon_url=ctx.guild.icon.url, name=ctx.guild.name)
    else:
        emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)

    view = Option(ctx)
    msg = await ctx.send(embed=emd, view=view)
    await view.wait()

    if view.value == 1:
        new = await msg.edit(
            embed=discord.Embed(
                description=f'{Emo.CHECK} You can now set `@everyone` as ping role'
                            f'\n\n{Emo.BELL} Please mention a **role** to set as **ping role:**'
            ),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=120)
            try:
                await new.delete()
            except discord.errors.NotFound:
                pass

            if '@everyone' in response.content:
                role = ctx.guild.default_role
                mention_string = role
            else:
                mentions = response.role_mentions
                role = mentions[0] if mentions else None
                mention_string = role.mention if role else '**None**'

            if role:
                await ctx.send(
                    content=f'{ctx.author.mention}',
                    embed=discord.Embed(
                        description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                                    f'new ping role is {mention_string}')
                )
                await db_push_object(guild_id=ctx.guild.id, item=[str(role.id)], key='arole')

            else:
                await ctx.send(embed=discord.Embed(description=f'{Emo.WARN} you did not mention a role'))
        except asyncio.TimeoutError:
            await ctx.send('Bye! you took so long')
    elif view.value == 2:
        await msg.edit(
            embed=discord.Embed(
                description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** ping role has been removed')
        )
        await db_push_object(guild_id=ctx.guild.id, item=['REMOVED'], key='arole')

    elif view.value == 0:
        try:
            await msg.delete()
        except discord.errors.NotFound:
            pass
