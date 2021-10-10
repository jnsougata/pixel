import asyncio
import asynctube
import discord
from discord.ext import commands
from src.extras.emojis import *
from src.extras.func import db_push_object, db_fetch_object



class ChannelMenu(discord.ui.Select):

    @classmethod
    async def create(
            cls,
            ctx: commands.Context,
            bot: discord.Client,
    ):

        raw = await db_fetch_object(
            guildId=ctx.guild.id,
            key='youtube'

        )
        if raw and len(raw['item']):
            options = [
                discord.SelectOption(
                    label=id,
                    emoji=Emo.YT
                ) for id in list(raw['item'])
            ]
        else:
            options = [
                discord.SelectOption(
                    label= 'No channel found',
                    emoji=Emo.YT
                )
            ]

        return cls(
            options = options,
            context = ctx,
            bot = bot
        )


    def __init__(
            self,
            context: commands.Context,
            bot:discord.Client,
            options: list = None,
    ):
        self.ctx = context
        self.bot = bot

        super().__init__(
            placeholder='Search results',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        pass


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot

        super().__init__()
        self.value = None


    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 'edit'
            self.stop()


    @discord.ui.button(label='Add', style=discord.ButtonStyle.blurple)
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 'add'
            self.stop()


    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = '_'
            self.stop()


class Confirmation(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot

        super().__init__()
        self.value = None


    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()


    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
            self.stop()










async def sub_view_youtube(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):

    emd = discord.Embed(
        description=f'**{ctx.guild.name}\'s** current set YouTube channels'
                    f'\nare in the drop down menu below'
                    f'\n\nTo set new channel tap **` Add `**'
                    f'\n\nTo remove old channel tap **` Edit `**'
    )
    emd.set_author(
        icon_url=ctx.guild.icon.url,
        name=ctx.guild.name
    )

    view = Option(ctx, bot)
    view.add_item(await ChannelMenu.create(ctx, bot))
    await interaction.response.edit_message(embed=emd, view=view)

    await view.wait()

    if view.value == 'edit':
        pass


    elif view.value == 'add':

        view.clear_items()

        new = await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please **type** a youtube channel ** Id or url:**'
            ),
            view=view
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=20)
            Id = response.content
            channel = await asynctube.Channel.fetch(Id)

            data = channel.info

            emd = discord.Embed(
                    title=f'{Emo.YT} {data["name"]}',
                    description=f'**` Subs `  {data["subscribers"]}**'
                                f'\n\n**` Views `  {data["views"]}**',
                    url=data["url"]
            )
            emd.set_thumbnail(url=data["avatar_url"])
            emd.set_image(url=data["banner_url"])

            new_view = Confirmation(ctx,bot)

            await new.edit(
                content=f'{ctx.author.mention}',
                embed=emd,
                view=new_view
            )

            await new_view.wait()

            if new_view.value is True:


                old_data = await db_fetch_object(
                    guildId=ctx.guild.id,
                    key='youtube'
                )

                latest = await channel.latest

                if old_data:
                    if len(old_data['item']) > 0:
                        raw = old_data['item']
                        raw[data['id']] = {'live': 'empty', 'upload': latest.id}

                        await db_push_object(
                            guildId=ctx.guild.id,
                            item=raw,
                            key='youtube'
                        )
                    else:
                        empty = dict()
                        empty[data['id']] = {'live': 'empty', 'upload': latest.id}
                        await db_push_object(
                            guildId=ctx.guild.id,
                            item=empty,
                            key='youtube'
                        )

                else:
                    empty = dict()
                    empty[data['id']] = {'live': 'empty', 'upload': latest.id}
                    await db_push_object(
                        guildId=ctx.guild.id,
                        item=empty,
                        key='youtube'
                    )
                await new.edit(content=f'{Emo.CHECK} {ctx.author.mention} **YouTube Channel added successfully!**')

            else:
                await interaction.delete_original_message()


        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')


    else:
        await interaction.delete_original_message()







