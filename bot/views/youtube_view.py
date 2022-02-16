import discord
import asyncio
from aiotube import Channel
from bot.extras.emojis import *
from extslash import ApplicationContext, Bot
from bot.extras.func import db_push_object, db_fetch_object


class Temp(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None


class ReceiverMenu(discord.ui.Select):

    def __init__(
            self,
            db_data: dict,
            youtube_info: dict,
            ctx: ApplicationContext,
    ):
        self.ctx = ctx
        self.db_data = db_data
        self.info = youtube_info
        channels = ctx.guild.text_channels
        eligible = [channel for channel in channels if channel.permissions_for(ctx.me).embed_links]
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id), emoji=Emo.TEXT)
            for channel in eligible[:24]
        ]
        options.insert(
            0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
        )
        super().__init__(placeholder='Select a text channel', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) != 0:
                emd = discord.Embed(
                    description=f'{Emo.YT} **[{self.info["name"]}]({self.info["url"]})**'
                                f'\n\n> {Emo.CHECK} YouTube channel added successfully'
                                f'\n> Bound to <#{self.values[0]}> for receiving notifications',
                    url=self.info['url'])
                await self.ctx.edit_response(embed=emd, view=None)
                self.db_data[self.info['id']] = str(self.values[0])
                await db_push_object(guild_id=self.ctx.guild.id, item=self.db_data, key='receivers')
            else:
                await self.ctx.delete_response()


class Confirmation(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
        self.ctx = ctx
        self.value = None
        super().__init__()

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
    def __init__(self, ctx: ApplicationContext):
        self.ctx = ctx
        self.value = None
        super().__init__()

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


async def sub_view_youtube(ctx: ApplicationContext, url: str):

    raw = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')

    def _check():
        if raw and raw[0].isdigit():
            return ctx.guild.get_channel(int(raw[0]))

    if raw and _check():

        old_data = await db_fetch_object(guild_id=ctx.guild.id, key='youtube')
        if old_data:
            total_channels = list(old_data)
        else:
            total_channels = []
        if len(total_channels) < 24:

            try:
                channel = Channel(url.replace(' ', ''))
                info = channel.info
                emd = discord.Embed(
                    title=f'{Emo.YT} {info["name"]}',
                    description=f'\n> **Subs:** {info["subscribers"]}'
                                f'\n> **Views:** {info["views"]}',
                    url=info["url"],
                    color=0xc4302b)
                banner_url = info.get('banner_url')
                avatar_url = info.get('avatar_url')
                if banner_url and banner_url.startswith('http'):
                    emd.set_image(url=banner_url)
                if avatar_url and avatar_url.startswith('http'):
                    emd.set_thumbnail(url=info["avatar_url"])
                new_view = Confirmation(ctx)
                await ctx.edit_response(embed=emd, view=new_view)
                await new_view.wait()
                if new_view.value:
                    if old_data:
                        old_data[info['id']] = {'live': 'empty', 'upload': channel.latest.id}
                        await db_push_object(guild_id=ctx.guild.id, item=old_data, key='youtube')
                    else:
                        empty = {info['id']: {'live': 'empty', 'upload': channel.latest.id}}
                        await db_push_object(guild_id=ctx.guild.id, item=empty, key='youtube')
                    text_select_view = TextSelection(ctx)
                    embed = discord.Embed(
                        title=f'Wait! one more step',
                        description=f'{Emo.TEXT} To use default receiver tap **`Default`**'
                                    f'\n\n{Emo.TEXT} To select another receiver tap **`Select`**',
                        color=0xc4302b)
                    await ctx.edit_response(embed=embed, view=text_select_view)
                    receivers = await db_fetch_object(guild_id=ctx.guild.id, key='receivers')
                    await text_select_view.wait()
                    if text_select_view.value == 0:
                        receiver = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')
                        if receiver and receiver[0].isdigit():
                            emd = discord.Embed(
                                description=f'{Emo.YT} **[{info["name"]}]({info["url"]})**'
                                            f'\n\n> {Emo.CHECK} YouTube channel added successfully'
                                            f'\n> Bound to <#{receiver[0]}> for receiving notifications',
                                url=info['url'])
                            await ctx.edit_response(embed=emd, view=None)
                        if receivers:
                            db_data = receivers
                        else:
                            db_data = {}
                        db_data[info['id']] = str(receiver[0])
                        await db_push_object(guild_id=ctx.guild.id, item=db_data, key='receivers')

                    elif text_select_view.value == 1:
                        emd = discord.Embed(
                            description=f'{Emo.TEXT} Select a text channel from the menu below:')
                        if receivers:
                            db_data = receivers
                        else:
                            db_data = {}
                        receiver_view = Temp()
                        receiver_view.add_item(ReceiverMenu(ctx=ctx, db_data=db_data, youtube_info=info))
                        await ctx.edit_response(embed=emd, view=receiver_view)
                else:
                    await ctx.delete_response()
            except Exception as e:
                if isinstance(e, asyncio.TimeoutError):
                    await ctx.edit_response('Bye! you took so long')
                else:
                    await ctx.edit_response(
                        embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'))
        else:
            await ctx.edit_response(
                embed=discord.Embed(
                    description=f'{Emo.WARN} You have exceeded the maximum allowed channels {Emo.WARN}'))

    else:
        emd = discord.Embed(
            title=f'{Emo.WARN} No Receiver Found {Emo.WARN}',
            description=f'Please set a default Text Channel '
                        f'\nfor receiving Livestream Notifications'
                        f'\n\n Don\'t worry! you can always assign specific'
                        f'\nText Channels for specific YouTube Channels'
                        f'\nonce you have a default Text Channel assigned'
                        f'\n\n**` Steps: `**'
                        f'\n\n**`/setup`**  select **`receiver`** from options')
        await ctx.edit_response(embed=emd, view=None)
