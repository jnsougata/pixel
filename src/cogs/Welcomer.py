import discord
from src.extras.card import *
from discord.ext import commands
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
        if raw and len(raw['item']) > 0:

            if raw['item'][0].isdigit():

                reception = await self.bot.get_channel(int(raw['item'][0]))

                urls = await db_fetch_object(
                    guildId=guildId,
                    key='cover'
                )

                if urls and len(urls['item']) > 0:
                    url = urls['item'][0]
                else:
                    url = 'https://i.imgur.com/CLy9KUO.jpg'

                bg_bytes = Io.fetch(url)
                avatar = member.avatar_url_as(format='png', size=256)
                buff = io.BytesIO()
                await avatar.save(buff)
                buff.seek(0)
                round_bg = Io.draw(size=(500, 500), color='white')
                canvas = Canvas(size=(620, 282), color='black')
                canvas.set_background(_byte=bg_bytes, _blur=True)
                canvas.add_round_image(_byte=round_bg, resize=(150, 150), position=(235, 30))
                canvas.add_round_image(_byte=buff, resize=(130, 130), position=(245, 40))
                canvas.add_text(
                    text=f'{member}',
                    font_pack='sans.ttf',
                    auto_align=True,
                    size=30,
                    position=(220, 180)
                )
                canvas.add_text(
                    text=f'You are {len(member.guild.members)}th Member',
                    font_pack='sans.ttf',
                    auto_align=True,
                    size=30,
                    position=(220, 215)
                )
                file = discord.File(canvas.output, 'author_card.png')
                emd = discord.Embed(description=f'**Welcome to {member.guild.name}**')
                emd.set_image(url="attachment://author_card.png")

                await reception.send(embed=emd, file=file)

        else:
            print(f'[Event:on_member_join | {member.guild.name} | No Welcome Channel]')






def setup(bot):
    bot.add_cog(Welcomer(bot))