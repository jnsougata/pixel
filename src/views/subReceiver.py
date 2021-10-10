import asyncio
import discord
from discord.ext import commands
from src.extras.emojis import *
from src.extras.func import db_push_object, db_fetch_object




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

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
            self.stop()




async def sub_view_receiver(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):

    raw = await db_fetch_object(
        guildId=ctx.guild.id,
        key='alertchannel'
    )

    try:
        receiver = ctx.guild.get_channel(int(raw['item'][0]))
        rm = receiver.mention
    except TypeError:
        rm = None
    emd = discord.Embed(
        description=f'**{ctx.guild.name}\'s** current receiver is {rm}'
                    f'\n\nTo set new receiver tap **` Edit `**'
    )
    emd.set_author(
        icon_url=ctx.guild.icon.url,
        name=ctx.guild.name
    )

    view = Option(ctx)
    await interaction.response.edit_message(embed=emd, view=view)

    await view.wait()

    if view.value is True:

        new = await interaction.message.edit(
            embed=discord.Embed(
                description='Please **mention** a text channel to use as **receiver:**'
            )
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=20)
            ls = response.channel_mentions
            if len(ls) > 0:
                await db_push_object(
                    guildId=ctx.guild.id,
                    item=[str(ls[0].id)],
                    key='alertchannel'
                )
                view.clear_items()
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.CHECK} **{ctx.guild.name}\'s** '
                                    f'new receiver channel is {ls[0].mention} ',
                    )
                )
            else:
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} Please mention a **text channel** properly!'
                    )
                )
        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')

    else:
        await interaction.delete_original_message()