import re
import aiotube
import app_util
import discord
import asyncio
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object


def has_perms(channel: discord.TextChannel, ctx: Context):
    bot_can = channel.permissions_for(ctx.me)
    return bot_can.send_messages and bot_can.embed_links and bot_can.use_external_emojis


class ReceiverSelection(discord.ui.Select):

    def __init__(self, ctx, info, data):
        self.ctx = ctx
        self.db_data = data
        self.info = info
        channels = ctx.guild.text_channels
        eligible = [channel for channel in channels if has_perms(channel, ctx)][:24]
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id), emoji=Emo.TEXT) for channel in eligible]
        options.insert(0, discord.SelectOption(label='default', value='0', emoji=Emo.TEXT))
        super().__init__(
            placeholder='select a text channel to set as receiver',
            min_values=1, max_values=1, options=options,
        )

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
                channel = aiotube.Channel(url.replace(' ', ''))
            except (aiotube.errors.InvalidURL, aiotube.errors.BadURL, aiotube.errors.AIOError):
                await ctx.send_followup(
                    embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'))
                return
            except aiotube.errors.TooManyRequests:
                await ctx.send_followup(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} you are requesting too often, try again in a few seconds'))
                return
            else:
                info = channel.info
                emd = discord.Embed(
                    title=f'{Emo.YT} {info["name"]}',
                    description=f'\n> **Subs:** {info["subscribers"]}\n> **Views:** {info["views"]}',
                    url=info["url"], color=0xc4302b)
                emd.set_footer(text='Select a text channel from the menu to receive notifications for current channel')
                banner_url = info.get('banner')
                avatar_url = info.get('avatar')
                if banner_url and banner_url.startswith('http'):
                    emd.set_image(url=banner_url)
                if avatar_url and avatar_url.startswith('http'):
                    emd.set_thumbnail(url=avatar_url)
                upload = channel.recent_uploaded
                upload_id = upload.id if upload else None
                if old_data:
                    old_data[info['id']] = {'live': 'empty', 'upload': upload_id or 'empty'}
                    await db_push_object(guild_id=ctx.guild.id, item=old_data, key='youtube')
                else:
                    empty = {info['id']: {'live': 'empty', 'upload': upload_id or 'empty'}}
                    await db_push_object(guild_id=ctx.guild.id, item=empty, key='youtube')

                receivers = await db_fetch_object(guild_id=ctx.guild.id, key='receivers')
                if receivers:
                    data = receivers
                else:
                    data = {}
                menu = discord.ui.View()
                menu.add_item(ReceiverSelection(ctx, info, data))
                await ctx.send_followup(embed=emd, view=menu)
        else:
            await ctx.send_followup(
                embed=discord.Embed(
                    description=f'{Emo.WARN} You have exceeded the number of maximum allowed channels {Emo.WARN}'))
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
