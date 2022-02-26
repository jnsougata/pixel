import io
import asyncio
import discord
import discord.errors
import airdrive.errors
from discord.ext import commands
from bot.extras.emojis import Emo
from bot.extras.card import Io, Canvas
from bot.extras.func import db_fetch_object, drive


class Listeners(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        bot_id = self.bot.user.id
        content_map = {
            f'<@!{bot_id}>': True,
            f'<@{bot_id}>': True,
            f'<@!{bot_id}> help': True,
            f'<@{bot_id}> help': True,
            f'<@!{bot_id}> setup': True,
            f'<@{bot_id}> setup': True,
        }
        if content_map.get(message.content.lower()):
            try:
                await message.channel.send(f'👀 I\'ve given up on prefixes! Please use {Emo.SLASH}')
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup folks! I\'m **{guild.me.display_name}**'
                        f'\n\nTo get started, send `/help`'
                        f'\n\nUse command `/setup` for everything'
                        f'\n\n**Important Links**'
                        f'\n[Invite]({invite}) - Add the bot to another server'
                        f'\n[Support Server]({support}) - Get some bot support here!',
            color=0xf2163b,
        )

        async def valid_intro_channel(_guild: discord.Guild):
            for channel in _guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    return channel

        intro = await valid_intro_channel(guild)

        if intro:
            try:
                await intro.send(embed=emd)
            except discord.errors.Forbidden:
                pass

        logger = self.bot.get_channel(899864601057976330)
        await logger.send(
            embed=discord.Embed(
                title=f'{Emo.MIC} {guild.name}',
                description=f'```\nMembers: {guild.member_count}'
                            f'\n\nID: {guild.id}\n```',
                colour=discord.Colour.blurple()
            )
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        registry = self.bot.get_channel(899864601057976330)
        await registry.send(
            embed=discord.Embed(
                title=f'{Emo.MIC} {guild.name}',
                description=f'```\nGuild ID: {guild.id}\n```',
                colour=discord.Colour.red()
            )
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.bot:
            guild_id = member.guild.id
            raw = await db_fetch_object(guild_id=guild_id, key='welcome')
            if raw and raw[0].isdigit():
                reception = member.guild.get_channel(int(raw[0]))
                if reception:

                    def get_background():
                        try:
                            path = f'covers/{guild_id}_card.png'
                            return io.BytesIO(drive.cache(path))
                        except airdrive.errors.FileNotFound:
                            return io.BytesIO(drive.cache('covers/default_card.png'))

                    loop = asyncio.get_event_loop()
                    bg_bytes = await loop.run_in_executor(None, get_background)
                    avatar = member.display_avatar.with_format('png')
                    bytes_ = await avatar.read()
                    round_bg = Io.draw(size=(1500, 1500), color='#FFFFFF')
                    canvas = Canvas(size=(1860, 846), color='black')
                    canvas.set_background(_byte=bg_bytes, _blur=True)
                    canvas.add_round_image(_byte=round_bg, resize=(420, 420), position=(720, 105))
                    canvas.add_round_image(_byte=io.BytesIO(bytes_), resize=(390, 390), position=(735, 120))
                    canvas.add_text(text=f'{member}', auto_align=True, size=90, position=(660, 540))
                    canvas.add_text(
                        size=90,
                        auto_align=True,
                        position=(660, 645),
                        text=f'You are {member.guild.member_count}th Member',
                    )
                    file = discord.File(canvas.output, 'hq_card.png')
                    scopes = {
                        '[ping.member]': '',
                        '[member.name]': str(member),
                        '[guild.name]': member.guild.name,
                        '[member.mention]': member.mention,
                    }

                    def converted(text: str):
                        for key, value in scopes.items():
                            text = text.replace(key, value)
                        return text

                    text_dict = await db_fetch_object(member.guild.id, 'text')
                    if text_dict and text_dict.get('welcome'):
                        raw_text = text_dict.get('welcome')
                        message = converted(text_dict.get('welcome'))
                    else:
                        raw_text = ' '
                        message = f'Welcome to **{member.guild.name}**'
                    emd = discord.Embed(description=message, color=0x303434)
                    emd.set_image(url="attachment://hq_card.png")
                    try:
                        if '[ping.member]' in raw_text:
                            await reception.send(content=member.mention, embed=emd, file=file)
                        else:
                            await reception.send(embed=emd, file=file)
                    except Exception:
                        pass


def setup(bot):
    bot.add_cog(Listeners(bot))
