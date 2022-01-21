import io
import discord
from discord.ext import commands
from src.extras.card import Io, Canvas
from src.extras.func import db_fetch_object, drive


class Welcomer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            guild_id = member.guild.id
            raw = await db_fetch_object(guild_id=guild_id, key='welcome')
            if raw and raw[0].isdigit():
                reception = member.guild.get_channel(int(raw[0]))
                if reception:
                    async def get_background():
                        try:
                            path = f'covers/{guild_id}_card.png'
                            return io.BytesIO(drive.cache(path))
                        except FileNotFoundError:
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
                    emd = discord.Embed(description=f'**Welcome to {member.guild.name}**', color=0x32353b)
                    emd.set_image(url="attachment://hq_card.png")
                    try:
                        await reception.send(embed=emd, file=file)
                    except Exception:
                        pass

        # this is only fot support server
            if guild_id == 834662394068336670:
                role = member.guild.get_role(838441883721924729)
                try:
                    await member.add_roles(role)
                except Exception:
                    pass


def setup(bot):
    bot.add_cog(Welcomer(bot))
