import re
import discord
from deta import Record
from deta.base import Base
from utils.emoji import Emo
from discord.ext import commands


class Listeners(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Base = bot.db  # type: ignore
        self.drive: Drive = bot.drive  # type: ignore

    @staticmethod
    def build_text(text: str, scopes: dict):
        for key, value in scopes.items():
            text = text.replace(key, value)
        return text

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        pattern = re.compile(f"^<@!?{self.bot.user.id}>")
        if message.author.bot:
            return
        result = pattern.search(message.content.lower())
        if not result:
            return
        try:
            await message.channel.send(f'👀 I\'ve given up on prefixes! Please use {Emo.SLASH}')
        except discord.errors.Forbidden:
            return

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.db.put(
            Record(
                {
                    'CUSTOM': None,
                    'CHANNELS': None,
                    'RECEIVER': None,
                    'PINGROLE': None,
                    'RECEPTION': None
                },
                key=str(guild.id)
            )
        )
        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup folks! I\'m **{guild.me}**'
                        f'\n\nTo get started, send `/help`'
                        f'\n\n**Important Links**'
                        f'\n[Invite]({invite}) - Add the bot to another server'
                        f'\n[Support Server]({support}) - Get some bot support here!',
            color=0x2f3136,
        )

        def any_text_channel():
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    return channel
        intro = any_text_channel()
        if not intro:
            return
        try:
            await intro.send(embed=emd)
        except discord.errors.Forbidden:
            pass
        logger = self.bot.get_channel(self.bot.log_channel_id)  # type: ignore
        await logger.send(
            f'```fix\n- Joined [{guild.name}](ID:{guild.id})'
            f'\n- Owner ID: {guild.owner_id}'
            f'\n- Member Count: {guild.member_count}```'
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.db.delete(str(guild.id))
        logger = self.bot.get_channel(self.bot.log_channel_id)  # type: ignore
        await logger.send(
            f'```diff\n- Removed [{guild.name}](ID:{guild.id})'
            f'\n- Owner ID: {guild.owner_id}'
            f'\n- Member Count: {guild.member_count}```'
        )


async def setup(bot):
    await bot.add_cog(Listeners(bot))
