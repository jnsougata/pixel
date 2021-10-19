import discord
import asyncio
import asynctube
from discord.ext import commands
from src.extras.emojis import *
from src.extras.func import db_push_object, db_fetch_object, prefix_fetcher


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

            async def name(Id: str):
                ch = await asynctube.Channel.fetch(Id)
                return ch.name

            ids = list(raw['item'])
            names = [await name(id) for id in list(raw['item'])]

            options = [
                discord.SelectOption(
                    label=names[i],
                    value=ids[i],
                    emoji=Emo.YT
                ) for i in range(len(ids))
            ]
            options.insert(
                0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
            )

        else:
            options = [
                discord.SelectOption(
                    label= 'Add a channel first',
                    emoji=Emo.WARN
                )
            ]

            options.insert(
                0, discord.SelectOption(label='Cancel', value='0', emoji=Emo.WARN)
            )

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

        if interaction.user == self.ctx.author:

            if int(self.values[0]) != 0:

                try:
                    raw = await asynctube.Channel.fetch(self.values[0])
                    data = raw.info

                    emd = discord.Embed(
                        title=f'{Emo.DEL} {data["name"]}',
                        description=f'**` Subs `  {data["subscribers"]}**'
                                    f'\n\n**` Views `  {data["views"]}**'
                                    f'\n\n**` Id `  {data["id"]}**',
                        url=data["url"]
                    )
                    emd.set_thumbnail(url=data["avatar_url"])
                    emd.set_image(url=data["banner_url"])
                    emd.set_footer(text='❌ This channel has been removed.')
                    await interaction.message.edit(
                        embed = emd,
                        view=None
                    )

                    db_raw = await db_fetch_object(
                        guildId=self.ctx.guild.id,
                        key='youtube'
                    )
                    new_data = db_raw['item']
                    new_data.pop(self.values[0])

                    await db_push_object(
                        guildId=self.ctx.guild.id,
                        item=new_data,
                        key='youtube'
                    )
                except AttributeError:
                    return

            else:
                await interaction.message.delete()


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot

        super().__init__()
        self.value = None


    @discord.ui.button(label='Add', style=discord.ButtonStyle.green)
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 'add'
            self.stop()


    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 'edit'
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
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()


    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
            self.stop()


class Temp(discord.ui.View):
    def __init__(self):
        self.message = None
        super().__init__()







async def sub_view_youtube(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    raw = await db_fetch_object(
        guildId=ctx.guild.id,
        key='alertchannel'
    )

    if raw and len(raw['item']) > 0:

        emd = discord.Embed(
            description=f'**{ctx.guild.name}\'s** YouTube channel Settings'
                        f'\n\nTo add new channel tap **` Add `**'
                        f'\n\nTo remove old channel tap **` Remove `**'
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

        view = Option(ctx, bot)
        await interaction.response.edit_message(embed=emd, view=view)

        await view.wait()

        if view.value == 'edit':
            view = Temp()
            view.add_item(await ChannelMenu.create(ctx, bot))

            await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description='Please select YouTube Channel to **remove:**'
                ),
                view=view
            )


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
                try:
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

                    await new.delete()

                    nxt = await ctx.send(
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
                        await nxt.edit(
                            content=f'{Emo.CHECK} {ctx.author.mention} **YouTube Channel added successfully!**',
                            view = None
                        )

                    else:
                        await interaction.delete_original_message()

                except AttributeError:
                    await interaction.delete_original_message()
                    await ctx.send(embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel Id or URL'))


            except asyncio.TimeoutError:
                await ctx.send('**Bye! you took so long**')


        else:
            try:
                await interaction.delete_original_message()
            except:
                return

    else:
        p = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Receiver Found {Emo.WARN}',
            description=f'Please Set a Text Channel '
                        f'\nfor receiving Livestream Notifications'
                        f'\n{p}setup -> select `receiver` from menu '
                        f'\n-> select `text channel option` from menu'
        )
        await interaction.response.edit_message(embed=emd, view=None)








