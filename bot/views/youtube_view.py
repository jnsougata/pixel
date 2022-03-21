import aiotube
import app_util
import discord
import asyncio
from aiotube import Channel
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object


async def autocomplete_channel(ctx: app_util.Context, youtube: str):
    if youtube:
        if youtube.startswith('http') and '/channel/' in youtube and len(youtube) > 55:
            url = youtube
        elif youtube.startswith('http') and '/c/' in youtube and len(youtube) > 26:
            url = youtube
        elif youtube.startswith('UC') and len(youtube) == 24:
            url = youtube
        else:
            url = None

        if url:
            try:
                channel = aiotube.Channel(url)
            except aiotube.errors.InvalidURL:
                choices = [app_util.Choice(name=f'Invalid channel ID or URL', value='null')]
                await ctx.send_automated_choices(choices)
            else:
                name = channel.name
                url = channel.url
                channel_id = channel.id
                choices = [app_util.Choice(name=f'{name} ({channel_id})', value=channel_id)]
                await ctx.send_automated_choices(choices)
        else:
            choices = [app_util.Choice(name=f'Can\'t find any channel...', value='null')]
            await ctx.send_automated_choices(choices)

    else:
        choices = [app_util.Choice(name=f'keep typing...', value='null')]
        await ctx.send_automated_choices(choices)


class ReceiverSelection(discord.ui.Select):

    def __init__(self, ctx, info, data):
        self.ctx = ctx
        self.db_data = data
        self.info = info
        channels = ctx.guild.text_channels
        eligible = [channel for channel in channels if channel.permissions_for(ctx.me).embed_links]
        options = [discord.SelectOption(label=channel.name, value=str(channel.id), emoji=Emo.TEXT)
                   for channel in eligible[:24]]
        options.insert(0, discord.SelectOption(label='DEFAULT', value='0', emoji=Emo.PING))
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
                default = await db_fetch_object(guild_id=self.ctx.guild.id, key='alertchannel')
                emd = discord.Embed(
                    description=f'{Emo.YT} **[{self.info["name"]}]({self.info["url"]})**'
                                f'\n\n> {Emo.CHECK} YouTube channel added successfully'
                                f'\n> Bound to <#{default[0]}> for receiving notifications',
                    url=self.info['url'])
                await self.ctx.edit_response(embed=emd, view=None)
                self.db_data[self.info['id']] = default[0]
                await db_push_object(guild_id=self.ctx.guild.id, item=self.db_data, key='receivers')


async def sub_view_youtube(ctx: Context, url: str):

    print('[YT]', url)

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
                channel = Channel(url)
                info = channel.info
                emd = discord.Embed(
                    title=f'{Emo.YT} {info["name"]}',
                    description=f'\n> **Subs:** {info["subscribers"]}\n> **Views:** {info["views"]}',
                    url=info["url"], color=0xc4302b)
                emd.set_footer(text='Select a text channel from the menu below to receive notifications')
                banner_url = info.get('banner_url')
                avatar_url = info.get('avatar_url')
                if banner_url and banner_url.startswith('http'):
                    emd.set_image(url=banner_url)
                if avatar_url and avatar_url.startswith('http'):
                    emd.set_thumbnail(url=info["avatar_url"])
                live = channel.recent_streamed
                upload = channel.recent_uploaded
                live_id = live.id if live else None
                upload_id = upload.id if upload else None
                if upload_id or live_id:
                    if old_data:
                        old_data[info['id']] = {'live': live_id or 'empty', 'upload': upload_id or 'empty'}
                        await db_push_object(guild_id=ctx.guild.id, item=old_data, key='youtube')
                    else:
                        empty = {info['id']: {'live': live_id or 'empty', 'upload': upload_id or 'empty'}}
                        await db_push_object(guild_id=ctx.guild.id, item=empty, key='youtube')
                else:
                    await ctx.edit_response(
                        embed=discord.Embed(
                            title=f'{Emo.WARN} No uploads found {Emo.WARN}',
                            description=f'No video has been found in this Channel!'
                                        f'\nPlease try with a channel with videos in it.'),
                        view=None)
                    return
                receivers = await db_fetch_object(guild_id=ctx.guild.id, key='receivers')
                if receivers:
                    data = receivers
                else:
                    data = {}
                menu = discord.ui.View()
                menu.timeout = 120
                menu.add_item(ReceiverSelection(ctx, info, data))
                await ctx.send_followup(embed=emd, view=menu)
            except Exception as e:
                print(e)
                if isinstance(e, asyncio.TimeoutError):
                    await ctx.send_followup('Bye! you took so long', view=None)
                else:
                    await ctx.send_followup(
                        embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'), view=None)
        else:
            await ctx.send_followup(
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
        await ctx.send_followup(embed=emd, view=None)
