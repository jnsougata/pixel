import os
import random
import logging
import asyncio
import aiohttp
import discord
import traceback
from utils.emoji import Emo
from typing import Optional
from itertools import islice
from deta import base, Updater
from discord.ext import commands, tasks


class Notifier(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.retry_bucket = []
        self.error_logger = None
        self.base: base.Base = bot.db  # noqa
        self.api_root = os.getenv('API_ROOT')
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.feed_checker.start()
    
    @staticmethod
    async def create_ping(guild: discord.guild, cache: dict) -> Optional[str]:
        role_id = cache[str(guild.id)].get('PINGROLE')
        if not (role_id and role_id.isdigit()):
            return
        role = guild.get_role(int(role_id))
        if not role:
            return
        if role == guild.default_role:
            return '@everyone'
        return role.mention
 
    @staticmethod
    async def create_receiver(guild: discord.Guild, youtube_id: str, cache: dict) -> Optional[discord.TextChannel]:
        try:
            receiver_id = cache[str(guild.id)]['CHANNELS'][youtube_id]['receiver']
        except KeyError:
            return
        else:
            if not (receiver_id and receiver_id.isdigit()):
                return
            return guild.get_channel(int(receiver_id))

    async def custom_message(
            self,
            guild: discord.Guild,
            channel_name: str,
            video_url: str,
            cache: dict
    ) -> Optional[str]:
        ping = await self.create_ping(guild, cache)
        scopes = {
            '[ping]': ping if ping else '',
            '[name]': channel_name,
            '[url]': video_url
        }
        data = cache[str(guild.id)].get('CUSTOM')
        if data and data.get("youtube"):
            text = data['youtube']
            if '[url]' not in text:
                text += f'\n{video_url}'
            for key, value in scopes.items():
                text = text.replace(key, value)
            return text
        return None

    @staticmethod
    async def log_exception(channel: discord.TextChannel, guild: discord.Guild, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await channel.send(embed=discord.Embed(
            title=f'{Emo.WARN} exception occurred during Task {Emo.WARN}',
            description=f'**Guild: {guild.name} | ID: {guild.id}**\n```py\n{tb}\n```'))

    async def on_feed_data(self, data: dict, cache: dict, guild: discord.Guild, proces_id: int):
        channel_name = data['channel_name']
        channel_id = data['channel_id']
        video_id = data['video_id']
        video_url = data['video_url']
        published_timestamp = int(data['video_published'])
        old_video_id = cache[str(guild.id)]['CHANNELS'][channel_id].get('recent', '')
        last_published_timestamp = int(cache[str(guild.id)]['CHANNELS'][channel_id].get('last_published', 0))
        if video_id == old_video_id:
            return
        if not (published_timestamp > last_published_timestamp):
            return
        subs = cache[str(guild.id)]['CHANNELS']
        subs[channel_id]['recent'] = video_id
        subs[channel_id]['last_published'] = data['video_published']
        try:
            updater = Updater()
            updater.set(f'CHANNELS.{channel_id}.recent', video_id)
            updater.set(f'CHANNELS.{channel_id}.last_published', data['video_published'])
            await self.base.update(str(guild.id), updater)
        except Exception as e:
            await self.log_exception(self.error_logger, guild, e)
        else:
            logging.info(f' [modf: {proces_id}] {guild.id} {channel_id}')
            content = await self.custom_message(guild, channel_name, video_url, cache)
            mention = await self.create_ping(guild, cache) or ''
            receiver = await self.create_receiver(guild, channel_id, cache)
            if not receiver:
                return
            if not content:
                content = (
                    f'> {Emo.YT} **{channel_name}** has a new content {mention}\n'
                    f'> Go check it out! {video_url}'
                )
            try:
                await asyncio.sleep(random.randint(1, 10))
                await receiver.send(content)
            except Exception as e:
                if not (isinstance(e, discord.errors.Forbidden) or isinstance(e, discord.errors.NotFound)):
                    await self.log_exception(self.error_logger, guild, e)
            else:
                logging.info(f' [sent: {proces_id}] {guild.id} {channel_id}')

    def subscription_groups(self, records: dict, length: int = 10) -> list:
        guilds = self.bot.guilds
        valid_records = [
            (records[str(guild.id)], guild)
            for guild in guilds if records.get(str(guild.id))
        ]
        valid_subs = [
            (guild, data['CHANNELS'])
            for data, guild in valid_records if data.get('CHANNELS')
        ]
        subs = [(channel_id, guild) for guild, subs in valid_subs for channel_id in subs]
        return [list(islice(subs, i, i + length)) for i in range(0, len(subs), length)]

    async def check_subscription(
            self,
            shard_id: int,
            channel_id: str,
            guild: discord.Guild,
            cache: dict
    ) -> None:
        await asyncio.sleep(random.randint(1, 30))
        url = self.api_root.format(shard_id) + f'/feed/{channel_id}'
        resp = await self.session.get(url)
        if resp.status != 200:
            logging.info(f' [fail: {shard_id}] {guild.id} {channel_id} <{resp.status}>')
            if not resp.status == 429:
                return
            await asyncio.sleep(random.randint(10, 30))
            return await self.check_subscription(shard_id, channel_id, guild, cache)
        else:
            data = await resp.json()
            data['channel_id'] = channel_id
            logging.info(f' [scan: {shard_id}] {guild.id} {channel_id}')
            return await self.on_feed_data(data, cache, guild, shard_id)

    async def check_subs_group(self, group: list, cache: dict):
        for i, (channel_id, guild) in enumerate(group):
            self.bot.loop.create_task(self.check_subscription(i, channel_id, guild, cache))

    async def inspect_groups(self, groups: list, cache: dict):
        for group in groups:
            await self.check_subs_group(group, cache)

    @tasks.loop(minutes=10)
    async def feed_checker(self):
        records = await self.base.fetch_all()
        data = {record.pop('key'): record for record in records}
        groups = self.subscription_groups(data)
        await self.inspect_groups(groups, data)
    
    @feed_checker.before_loop
    async def before_start(self):
        await self.bot.wait_until_ready()
        chan_id = os.getenv('LOG_CHANNEL')
        if chan_id and chan_id.isdigit():
            self.error_logger = self.bot.get_channel(int(chan_id))
        else:
            logging.warning(' {LOG_CHANNEL} is not set in env. In-server logging will not work.')
        if not self.api_root:
            logging.warning(' {API_ROOT} is not set in env. Can not proceed further.')
            self.feed_checker.stop()
 

async def setup(bot: commands.Bot):
    await bot.add_cog(Notifier(bot))
