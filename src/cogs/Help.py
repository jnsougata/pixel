import discord
from src.extras.func import *
from discord.ext import commands
from src.extras.emojis import Emo


class CustomView(discord.ui.View):
    def __init__(
            self,
            ctx: commands.Context,
            message: discord.Message = None
    ):
        self.ctx = ctx
        self.message = message

        INVITE = discord.ui.Button(
            label='Invite',
            style=discord.ButtonStyle.link,
            url='https://top.gg/bot/848304171814879273/invite'
        )
        super().__init__()
        self.value = None
        self.timeout = 60
        self.add_item(INVITE)

    @discord.ui.button(label='Info', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except Exception as e:
            print(e)
            return


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.member)
    async def help(self, ctx: commands.Context):
        p = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            description=f''
                        f'\n\n{Emo.SETTINGS} To set me up'
                        f'\n use command **{p}setup**'
                        f'\n\n{Emo.FAQ} To know more'
                        f'\nabout **setup** tap **`Info`**'
                        f'\n\n{Emo.SUP} Join **[PixeL Support]'
                        f'(https://discord.gg/UzyEYeYZF9)**'
                        f'\n​‍‍‍',
            color=0x005aef
        )
        emd.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar.url
        )
        emd.set_footer(
            text=f'✅ Thanks | Current Prefix [{p}]',
        )

        view = CustomView(ctx)
        view.message = await ctx.send(embed=emd, view=view)

        await view.wait()

        if view.value:

            emd = discord.Embed(
                description=f'{Emo.INFO} Access all of these'
                            f'\nfollowing options by only using **{p}setup**'
                            f'\n\n{Emo.TAG}**Prefix**'
                            f'\nUsed to add or remove custom prefix '
                            f'\nto your server. you can change it anytime'
                            f'\n\n{Emo.PING} **Receiver**'
                            f'\nUsed to add or remove a text channel'
                            f'\nto receive youtube alerts for your server'
                            f'\n\n{Emo.YT} **YouTube**'
                            f'\nUsed to add or remove youtube'
                            f'\nchannel to your server for live alerts'
                            f'\n\n{Emo.DEAL} **Reception**'
                            f'\nUsed to add or remove a text'
                            f'\nchannel for receiving welcome cards'
                            f'\n\n{Emo.IMG} **Welcome Card**'
                            f'\nUsed to add or remove a welcome card'
                            f'\nfor your server to welcome new members',
                color=0x005aef,
            )
            emd.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            await view.message.edit(embed=emd, view=None)


def setup(bot):
    bot.add_cog(Help(bot))
