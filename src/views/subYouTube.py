import discord
import asyncio
from aiotube import Channel
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_push_object, db_fetch_object, db_fetch_prefix


class Temp(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None


class ReceiverMenu(discord.ui.Select):

    def __init__(
            self,
            db_data: dict,
            youtube_info: dict,
            bot: discord.Client,
            context: commands.Context,
    ):
        self.bot = bot
        self.ctx = context
        self.db_data = db_data
        self.info = youtube_info
        channels = context.guild.text_channels
        eligible = [
            channel for channel in channels if channel.permissions_for(
                context.guild.me
            ).embed_links
        ]
        options = [discord.SelectOption(
            label=channel.name, value=str(channel.id), emoji=Emo.TEXT
        ) for channel in eligible[:24]
        ]
        options.insert(
            0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
        )
        super().__init__(
            placeholder='Select a text channel',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) != 0:
                channel = self.bot.get_channel(int(self.values[0]))
                emd = discord.Embed(
                    title=f'{Emo.YT} {self.info["name"]}',
                    description=f'{Emo.CHECK} The receiver channel is {channel.mention}'
                                f'\nThis channel will be used to receive livestream & upload notifications',
                    url=self.info['url'],
                )
                await interaction.message.edit(embed=emd, view=None)
                self.db_data[self.info['id']] = str(self.values[0])
                await db_push_object(guild_id=self.ctx.guild.id, item=self.db_data, key='receivers')
            else:
                await interaction.message.delete()


class ChannelMenu(discord.ui.Select):

    @classmethod
    async def display(cls, bot: discord.Client, ctx: commands.Context, db_data: dict):
        raw = await db_fetch_object(guild_id=ctx.guild.id, key='youtube')
        if raw:
            ids = list(raw)
            names = [Channel(id).name for id in list(raw)]
            options = [discord.SelectOption(label=names[i], value=ids[i], emoji=Emo.YT) for i in range(len(ids))]
            options.insert(0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS))
        else:
            options = [discord.SelectOption(label='Please add a channel', emoji=Emo.WARN)]
            options.insert(0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS))

        return cls(bot=bot, ctx=ctx, options=options, db_data=db_data)

    def __init__(self, bot: discord.Client, ctx: commands.Context, options: list, db_data: dict):
        self.bot = bot
        self.ctx = ctx
        self.db_data = db_data

        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
            placeholder='Search results'
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if self.values[0] != '0':
                ch = Channel(self.values[0])
                data = ch.info
                emd = discord.Embed(
                    title=f'❌ {data["name"]}',
                    description=f'**` Subs `  {data["subscribers"]}**'
                                f'\n\n**` Views `  {data["views"]}**'
                                f'\n\n**` Id `  {data["id"]}**',
                    url=data["url"],
                    color=0xc4302b)
                if data["avatar_url"] and data["banner_url"]:
                    emd.set_thumbnail(url=data["avatar_url"])
                    emd.set_image(url=data["banner_url"])
                await interaction.message.edit(embed=emd, view=None)
                db_raw = await db_fetch_object(guild_id=self.ctx.guild.id, key='youtube')
                db_raw.pop(self.values[0])
                await db_push_object(guild_id=self.ctx.guild.id, item=db_raw, key='youtube')
                self.db_data.pop(self.values[0], None)
                await db_push_object(guild_id=self.ctx.guild.id, item=self.db_data, key='receivers')
            else:
                await interaction.message.delete()


class MainOption(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot
        super().__init__()
        self.value = None

    @discord.ui.button(label='Add', style=discord.ButtonStyle.green)
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 0
            self.stop()


class Confirmation(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.bot = bot
        self.value = None
        super().__init__()
        self.message = None

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


class TextSelection(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.bot = bot
        self.value = None
        super().__init__()
        self.message = None

    @discord.ui.button(label='Default', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 0
            self.stop()

    @discord.ui.button(label='Select', style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()


async def sub_view_youtube(
        bot: discord.Client,
        ctx: commands.Context,
        interaction: discord.Interaction
):
    raw = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')

    def _check():
        if raw and raw[0].isdigit():
            return ctx.guild.get_channel(int(raw[0]))

    if raw and _check():
        emd = discord.Embed(
            description=f'**{ctx.guild.name}\'s** YouTube settings'
                        f'\n\nTo add new channel tap **`Add`**'
                        f'\n\nTo remove old channel tap **`Remove`**',
            color=0xc4302b
        )
        if ctx.guild.icon:
            emd.set_author(icon_url=ctx.guild.icon.url, name=ctx.guild.name)
        else:
            emd.set_author(icon_url=ctx.guild.me.avatar.url, name=ctx.guild.me.name)

        view = MainOption(ctx, bot)
        await interaction.response.edit_message(embed=emd, view=view)
        await view.wait()

        if view.value == 1:
            view.clear_items()
            new = await interaction.message.edit(
                embed=discord.Embed(description='Please type a youtube channel **ID** or **URL:**', color=0xc4302b),
                view=view
            )

            def check(m):
                return m.author == ctx.author

            try:
                response = await bot.wait_for('message', check=check, timeout=20)
                channel = Channel(response.content)
                try:
                    info = channel.info
                    emd = discord.Embed(title=f'{Emo.YT} {info["name"]}',
                                        description=f'**` Subs `  {info["subscribers"]}**'
                                        f'\n\n**` Views `  {info["views"]}**', url=info["url"],
                                        color=0xc4302b)
                    if info["avatar_url"] and info["banner_url"]:
                        emd.set_thumbnail(url=info["avatar_url"])
                        emd.set_image(url=info["banner_url"])
                    await new.delete()
                    new_view = Confirmation(ctx, bot)
                    nxt = await ctx.send(embed=emd, view=new_view)
                    await new_view.wait()
                    if new_view.value:
                        old_data = await db_fetch_object(guild_id=ctx.guild.id, key='youtube')
                        if old_data:
                            old_data[info['id']] = {'live': 'empty', 'upload': channel.latest.id}
                            await db_push_object(guild_id=ctx.guild.id, item=old_data, key='youtube')
                        else:
                            empty = {info['id']: {'live': 'empty', 'upload': channel.latest.id}}
                            await db_push_object(guild_id=ctx.guild.id, item=empty, key='youtube')
                        text_select_view = TextSelection(ctx, bot)
                        embed = discord.Embed(
                            title=f'Wait! one more step',
                            description=f'{Emo.TEXT} To use default receiver tap **`Default`**'
                                        f'\n\n{Emo.TEXT} To select another receiver tap **`Select`**',
                            color=0xc4302b)
                        await nxt.edit(embed=embed, view=text_select_view)
                        receivers = await db_fetch_object(guild_id=ctx.guild.id, key='receivers')
                        await text_select_view.wait()

                        if text_select_view.value == 0:
                            receiver = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')
                            if receiver and receiver[0].isdigit():
                                channel = bot.get_channel(int(receiver[0]))
                                emd = discord.Embed(
                                    title=f'{Emo.YT} {info["name"]}',
                                    description=f'{Emo.CHECK} The receiver channel is {channel.mention}'
                                                f'\nThis channel will be used to receive livestream & upload '
                                                f'notifications',
                                    url=info['url'],
                                )
                                await nxt.edit(embed=emd, view=None)
                            if receivers:
                                db_data = receivers
                            else:
                                db_data = {}
                            db_data[info['id']] = str(receiver[0])
                            await db_push_object(guild_id=ctx.guild.id, item=db_data, key='receivers')

                        elif text_select_view.value == 1:
                            emd = discord.Embed(description=f'{Emo.TEXT} Select a text channel from the menu below:')
                            if receivers:
                                db_data = receivers
                            else:
                                db_data = {}
                            receiver_view = Temp()
                            receiver_view.add_item(ReceiverMenu(
                                bot=bot, context=ctx, db_data=db_data, youtube_info=info))
                            await nxt.edit(embed=emd, view=receiver_view)
                    else:
                        await nxt.delete()
                except Exception as e:
                    print(e)
                    await ctx.send(embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel Id or URL'))

            except asyncio.TimeoutError:
                await ctx.send('Bye! you took so long')

        elif view.value == 2:
            receivers = await db_fetch_object(guild_id=ctx.guild.id, key='receivers')
            if receivers:
                db_data = receivers
            else:
                db_data = {}
            view = Temp()
            view.add_item(await ChannelMenu.display(bot=bot, ctx=ctx, db_data=db_data))
            await interaction.message.edit(
                embed=discord.Embed(description='Please select YouTube Channel to **remove:**', color=0xc4302b),
                view=view
            )

        elif view.value == 0:
            await interaction.message.delete()
    else:
        prefix = await db_fetch_prefix(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Receiver Found {Emo.WARN}',
            description=f'Please set a Text Channel '
                        f'\nfor receiving Livestream Notifications'
                        f'\n\n**`Steps`**'
                        f'\n**{prefix}setup**  select **receiver** from menu '
                        f'\nThen tap **Edit**  select **text channel** from menu'
        )
        await interaction.response.edit_message(embed=emd, view=None)
