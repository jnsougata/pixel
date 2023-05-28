import io
import re
import deta
import discord
from deta import Record
from deta.base import Base
from deta.drive import Drive
from utils.emoji import Emo
from utils.canvas import Canvas
from discord.ext import commands
from PIL import UnidentifiedImageError


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

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        guild_id = member.guild.id
        try:
            record = await self.db.get(str(guild_id))
        except deta.NotFound:
            return
        reception_id = record.get('RECEPTION')
        if not (reception_id and reception_id.isdigit()):
            return
        reception = member.guild.get_channel(int(reception_id))
        if not reception:
            return
        canvas = Canvas(1860, 846)
        canvas.load_fonts('utils/ballad.ttf')
        try:
            stream = await self.drive.get(f'covers/{guild_id}_card.png')
            background = canvas.to_image(io.BytesIO(await stream.read()))
            canvas.set_background(img=background, blur_level=2)
        except (deta.NotFound, UnidentifiedImageError, ValueError):
            stream = await self.drive.get('covers/default_card.png')
            background = canvas.to_image(io.BytesIO(await stream.read()))
            canvas.set_background(img=background, blur_level=2)
        avatar = member.display_avatar.with_format('png')
        avatar_img = canvas.to_image(io.BytesIO(await avatar.read()))
        accent_color = canvas.get_accent(avatar_img)
        accent_background = Canvas(1500, 1500, accent_color).as_img()
        canvas.draw_round_image(img=accent_background, resize_x=420, resize_y=420, position_left=720, position_top=105)
        canvas.draw_round_image(img=avatar_img, resize_x=390, resize_y=390, position_left=735, position_top=120)
        canvas.draw_text(text=str(member), font_size=50, top=540, font_color="#FFFFFF")
        canvas.draw_text(
            text=f'You are {member.guild.member_count}th Member', font_size=60, top=650, font_color='white')
        file = discord.File(canvas.to_bytes(), 'welcome.png')
        scopes = {
            '[ping.member]': '',
            '[member.name]': str(member),
            '[guild.name]': member.guild.name,
            '[member.mention]': member.mention,
        }
        custom_text = record.get('CUSTOM')
        if custom_text and custom_text.get('welcome'):
            text = custom_text['welcome']
            message = self.build_text(text, scopes)
        else:
            text = '[no.ping]'
            message = f'**Welcome to {member.guild.name}**'
        emd = discord.Embed(description=message, color=0x2f3136)
        emd.set_image(url="attachment://welcome.png")
        try:
            if '[ping.member]' in text:
                await reception.send(content=member.mention, embed=emd, file=file)
            else:
                await reception.send(embed=emd, file=file)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass


async def setup(bot):
    await bot.add_cog(Listeners(bot))
