import asyncio
import discord
from discord.ext import commands
from src.extras.emojis import *
from src.extras.func import prefix_fetcher, db_push_object







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




async def sub_view_prefix(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    p = await prefix_fetcher(ctx.guild.id)

    emd = discord.Embed(
        description=f'**{ctx.guild.me.display_name}\'s** current prefix is **` {p} `**'
                    f'\n\nTo set new custom prefix tap **` Edit `**'
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
                description='Please **type** a prefix to set as **custom prefix:**'
            )
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=20)
            if 0 < len(response.content) <= 3:
                await db_push_object(
                    guildId=ctx.guild.id,
                    item=[response.content],
                    key='prefix'
                )
                view.clear_items()
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                                    f'new custom prefix is  ` {response.content} `',
                    )
                )
            else:
                await new.edit(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} Please try with **3** or **less** characters!'
                    )
                )
        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')

    else:
        await interaction.delete_original_message()