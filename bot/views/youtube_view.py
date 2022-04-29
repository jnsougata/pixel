import aiotube
import app_util
import discord
import asyncio
from asyncdeta import Field
from bot.extras.emojis import *
from app_util import Context, Bot


def has_perms(channel: discord.TextChannel, ctx: Context):
    bot_can = channel.permissions_for(ctx.me)
    return bot_can.send_messages and bot_can.embed_links and bot_can.use_external_emojis


class ReceiverSelection(discord.ui.Select):

    def __init__(self, bot, ctx, info):
        self.bot = bot
        self.ctx = ctx
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
                self.bot.cached[self.ctx.guild.id]['CHANNELS'][self.info['id']]['receiver'] = str(self.values[0])
            else:
                default = self.bot.cached[self.ctx.guild.id]['RECEIVER']
                emd = discord.Embed(
                    description=f'{Emo.YT} **[{self.info["name"]}]({self.info["url"]})**'
                                f'\n\n> {Emo.CHECK} YouTube channel added successfully'
                                f'\n> Bound to <#{default}> for receiving notifications',
                    url=self.info['url'])
                await self.ctx.edit_response(embed=emd, view=None)
                self.bot.cached[self.ctx.guild.id]['CHANNELS'][self.info['id']]['receiver'] = default

            await self.bot.db.add_field(
                key=str(self.ctx.guild.id),
                field=Field(name='CHANNELS', value=self.bot.cached[self.ctx.guild.id]['CHANNELS']),
                force=True
            )


async def sub_view_youtube(bot: Bot, ctx: Context, url: str):

    receiver = bot.cached[ctx.guild.id].get('RECEIVER')

    if receiver and receiver.isdigit() and ctx.guild.get_channel(int(receiver)):
        old_data = bot.cached[ctx.guild.id].get('CHANNELS')
        if old_data:
            total_channels = len(list(old_data))
        else:
            total_channels = 0
        if total_channels <= 23:
            try:
                channel = aiotube.Channel(url.replace(' ', ''))
                info = channel.info
            except (aiotube.errors.InvalidURL, aiotube.errors.BadURL, aiotube.errors.AIOError):
                await ctx.send_followup(
                    embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'))
            except aiotube.errors.TooManyRequests:
                await ctx.send_followup(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} you are requesting too often, try again in a few seconds'))
            else:
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
                    bot.cached[ctx.guild.id]['CHANNELS'][info['id']] = {
                        'live': 'empty', 'upload': upload_id or 'empty'
                    }
                else:
                    bot.cached[ctx.guild.id]['CHANNELS'] = {
                        info['id']: {'live': 'empty', 'upload': upload_id or 'empty'}
                    }
                menu = discord.ui.View()
                menu.add_item(ReceiverSelection(bot, ctx, info))
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
