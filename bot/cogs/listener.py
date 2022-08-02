import io
import asyncio
import discord
from asyncdeta import Field
from discord.ext import commands
from bot.extras.emojis import Emo
from PIL import UnidentifiedImageError
from imgen import Canvas


class Listeners(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        bot_id = self.bot.user.id
        content_map = {
            f'<@!{bot_id}>': True, f'<@{bot_id}>': True, f'<@!{bot_id}> help': True,
            f'<@{bot_id}> help': True, f'<@!{bot_id}> setup': True, f'<@{bot_id}> setup': True,
        }
        if content_map.get(message.content.lower()):
            try:
                await message.channel.send(f'👀 I\'ve given up on prefixes! Please use {Emo.SLASH}')
            except discord.errors.Forbidden:
                return

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        self.bot.cached[guild.id] = {
            'CUSTOM': None, 'CHANNELS': None, 'RECEIVER': None, 'PINGROLE': None, 'RECEPTION': None
        }

        await self.bot.db.put_many(
            key=str(guild.id),
            fields=[
                Field('CUSTOM', None), Field('CHANNELS', None),
                Field('RECEIVER', None), Field('PINGROLE', None), Field('RECEPTION', None),
            ]
        )

        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup folks! I\'m **{guild.me}**'
                        f'\n\nTo get started, send `/help`'
                        f'\n\nUse command `/setup` for everything'
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
        if intro:
            try:
                await intro.send(embed=emd)
            except discord.errors.Forbidden:
                pass

        logger = self.bot.get_channel(899864601057976330)
        await logger.send(f'```fix\n- Joined [{guild.name}](ID:{guild.id})'
                          f'\n- Owner ID: {guild.owner_id}'
                          f'\n- Member Count: {guild.member_count}```')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.cached.pop(guild.id, None)
        await self.bot.db.delete(str(guild.id))
        logger = self.bot.get_channel(899864601057976330)
        await logger.send(f'```diff\n- Removed [{guild.name}](ID:{guild.id})'
                          f'\n- Owner ID: {guild.owner_id}'
                          f'\n- Member Count: {guild.member_count}```')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if not member.bot:
            guild_id = member.guild.id
            cached = self.bot.cached.get(guild_id)
            reception_id = cached.get('RECEPTION') if cached else None

            if reception_id and reception_id.isdigit():
                reception = member.guild.get_channel(int(reception_id))
                if reception:
                    try:
                        bg = await self.bot.drive.get(f'covers/{guild_id}_card.png')
                    except:
                        bg = await self.bot.drive.get('covers/default_card.png')
                    avatar = member.display_avatar.with_format('png')
                    avatar_io = io.BytesIO(await avatar.read())
                    canvas = Canvas(1860, 846)
                    canvas.load_fonts('bot/extras/ballad.ttf')
                    try:
                        canvas.background(path=bg, blur_level=5)
                    except UnidentifiedImageError:
                        bg = await self.bot.drive.get('covers/default_card.png')
                        canvas.background(path=bg, blur_level=5)
                    accent_color = canvas.get_accent(avatar_io)
                    accent = Canvas(1500, 1500, accent_color).read()
                    canvas.round_image(path=accent, resize_x=420, resize_y=420, position_left=720, position_top=105)
                    canvas.round_image(path=avatar_io, resize_x=390, resize_y=390, position_left=735, position_top=120)
                    canvas.text(text=str(member), font_size=50, position_top=540, font_color="#FFFFFF")
                    canvas.text(text=f'You are {member.guild.member_count}th Member',
                                font_size=60, position_top=650, font_color=accent_color)
                    file = discord.File(canvas.read(), 'card_hq.png')
                    scopes = {
                        '[ping.member]': '',
                        '[member.name]': str(member),
                        '[guild.name]': member.guild.name,
                        '[member.mention]': member.mention,
                    }

                    def build_text(text: str):
                        for key, value in scopes.items():
                            text = text.replace(key, value)
                        return text

                    custom_text = self.bot.cached[guild_id].get('CUSTOM')
                    if custom_text and custom_text.get('welcome'):
                        plain_text = custom_text['welcome']
                        message = build_text(plain_text)
                    else:
                        plain_text = '[no.ping]'
                        message = f'**Welcome to {member.guild.name}**'
                    emd = discord.Embed(description=message, color=0x2f3136)
                    emd.set_image(url="attachment://card_hq.png")
                    try:
                        if '[ping.member]' in plain_text:
                            await reception.send(content=member.mention, embed=emd, file=file)
                        else:
                            await reception.send(embed=emd, file=file)
                    except (discord.errors.Forbidden, discord.errors.HTTPException):
                        pass


async def setup(bot):
    await bot.add_cog(Listeners(bot))
