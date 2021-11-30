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
        guildId = member.guild.id
        raw = await db_fetch_object(
            guildId=guildId,
            key='welcome'
        )
        if raw and raw['item'] > 0:
            if raw['item'][0].isdigit():
                reception = self.bot.get_channel(int(raw['item'][0]))
                urls = await db_fetch_object(
                    guildId=guildId,
                    key='cover'
                )
                if urls and urls['item']:
                    url = urls['item'][0]
                else:
                    url = 'https://i.imgur.com/CLy9KUO.jpg'
                if url != 'removed':
                    bg_bytes = await Io.fetch(url)
                    avatar = member.display_avatar.with_format('png')
                    bytes_ = await avatar.read()
                    round_bg = Io.draw(size=(500, 500), color='#ed0d45')
                    canvas = Canvas(size=(620, 282), color='black')
                    canvas.set_background(_byte=bg_bytes, _blur=True)
                    canvas.add_round_image(_byte=round_bg, resize=(140, 140), position=(240, 35))
                    canvas.add_round_image(_byte=io.BytesIO(bytes_), resize=(130, 130), position=(245, 40))
                    canvas.add_text(
                        text=f'{member}',
                        auto_align=True,
                        size=30,
                        position=(220, 180)
                    )
                    canvas.add_text(
                        text=f'You are {len(member.guild.members)}th Member',
                        auto_align=True,
                        size=30,
                        position=(220, 215)
                    )
                    file = discord.File(canvas.output, 'welcome_card.png')
                    emd = discord.Embed(description=f'**Welcome to {member.guild.name}**')
                    emd.set_image(url="attachment://welcome_card.png")
                    await reception.send(embed=emd, file=file)
                else:
                    print(f'[Event:on_member_join | {member.guild.name} | No Welcome Card]')
        else:
            pass


def setup(bot):
    bot.add_cog(Welcomer(bot))
