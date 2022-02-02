import io
import discord
import discord.errors
from discord.ext import commands
from src.extras.emojis import Emo
import airdrive.errors
from src.extras.card import Io, Canvas
from src.extras.func import db_fetch_object, drive


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup folks! I\'m **{guild.me.display_name}**'
                        f'\n\nTo get started, send `.help` | `@{guild.me.display_name} help` '
                        f'\n\nUse any one commands for everything:'
                        f'\n`/setup` | `.setup`'
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
                description=f'```\nOwner: {guild.owner}'
                            f'\n\nMembers: {guild.member_count}'
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
                description=f'```\nInspect for suspicious activity\nGuild ID: {guild.id}\n```',
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
                    async def get_background():
                        try:
                            path = f'covers/{guild_id}_card.png'
                            return io.BytesIO(drive.cache(path))
                        except airdrive.errors.FileNotFound:
                            return io.BytesIO(drive.cache('covers/default_card.png'))

                    bg_bytes = await get_background()
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
                    emd = discord.Embed(description=f'**Welcome to {member.guild.name}**', color=0x303434)
                    emd.set_image(url="attachment://hq_card.png")
                    try:
                        await reception.send(embed=emd, file=file)
                    except Exception:
                        pass

            if guild_id == 834662394068336670:
                # this is only for support server
                #  not to be used in others
                role = member.guild.get_role(838441883721924729)
                try:
                    await member.add_roles(role)
                except Exception:
                    pass


def setup(bot):
    bot.add_cog(Listeners(bot))
