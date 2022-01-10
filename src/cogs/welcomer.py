import io
import discord
from discord.ext import commands
from src.extras.card import Io, Canvas
from src.extras.func import db_fetch_object


class Welcomer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        raw = await db_fetch_object(guild_id=guild_id, key='welcome')

        if raw and raw[0].isdigit():
            reception = self.bot.get_channel(int(raw[0]))
            urls = await db_fetch_object(guild_id=guild_id, key='cover')
            if urls:
                url = urls[0]
            else:
                url = 'https://i.imgur.com/CLy9KUO.jpg'

            if url.startswith('http'):
                bg_bytes = await Io.fetch(url)
                if bg_bytes:
                    avatar = member.display_avatar.with_format('png')
                    bytes_ = await avatar.read()
                    round_bg = Io.draw(size=(1500, 1500), color='#FFFFFF')
                    canvas = Canvas(size=(1860, 846), color='black')
                    canvas.set_background(_byte=bg_bytes, _blur=True)
                    canvas.add_round_image(_byte=round_bg, resize=(420, 420), position=(720, 105))
                    canvas.add_round_image(_byte=io.BytesIO(bytes_), resize=(390, 390), position=(735, 120))
                    canvas.add_text(
                        text=f'{member}',
                        auto_align=True,
                        size=90,
                        position=(660, 540)
                    )
                    canvas.add_text(
                        text=f'You are {len(member.guild.members)}th Member',
                        auto_align=True,
                        size=90,
                        position=(660, 645)
                    )
                    file = discord.File(canvas.output, 'welcome_card.png')
                    emd = discord.Embed(description=f'**Welcome to {member.guild.name}**')
                    emd.set_image(url="attachment://welcome_card.png")
                    if reception:
                        try:
                            await reception.send(embed=emd, file=file)
                        except discord.errors.Forbidden:
                            print(f'[Event:on_member_join | {member.guild.name} | No Permission]')
                    else:
                        print(f'[Event:on_member_join | {member.guild.name} | No Reception Found]')
            else:
                print(f'[Event:on_member_join | {member.guild.name} | No Welcome Card]')


def setup(bot):
    bot.add_cog(Welcomer(bot))
