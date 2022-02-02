import discord
from discord.ext import commands
from src.extras.emojis import Emo
from src.extras.func import db_fetch_prefix


class CustomView(discord.ui.View):
    def __init__(
            self,
            ctx: commands.Context,
            message: discord.Message = None
    ):
        self.ctx = ctx
        self.message = message

        invite = discord.ui.Button(
            label='Invite',
            style=discord.ButtonStyle.link,
            url='https://top.gg/bot/848304171814879273/invite'
        )
        upvote = discord.ui.Button(
            label='Upvote',
            style=discord.ButtonStyle.link,
            url='https://top.gg/bot/848304171814879273/vote'
        )

        super().__init__()
        self.value = None
        self.timeout = 120
        self.add_item(invite)
        self.add_item(upvote)

    @discord.ui.button(label='Info', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except Exception:
            pass


class Help(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(name='help')
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.member)
    async def help(self, ctx: commands.Context):
        prefix = await db_fetch_prefix(ctx.guild.id)
        emd = discord.Embed(
            description=f'\n\n{Emo.SETUP} Start setup using **`{prefix}setup`** or **`/setup`**'
                        f'\n\n{Emo.FAQ} To know more about **setup** tap **`Info`**'
                        f'\n\n{Emo.SUP} Having issues? Join **[Dev & Support](https://discord.gg/VE5qRFfmG2)**',
            color=0x005aef)

        view = CustomView(ctx)
        view.message = await ctx.send(embed=emd, view=view)

        await view.wait()
        if view.value:

            emd = discord.Embed(
                description=f'{Emo.INFO} Access all of these'
                            f'\nfollowing options by only using **/setup**'
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
                            f'\n\n{Emo.BELL} **Role Ping**'
                            f'\nUsed to add or remove a custom role'
                            f'\nto be mentioned with the YT Notifications'
                            f'\n\n{Emo.IMG} **Welcome Card**'
                            f'\nUsed to add or remove a welcome card'
                            f'\nfor your server to welcome new members'
                            f'\n\n{Emo.CUSTOM} **Customize Message**'
                            f'\nUsed to add or remove a custom message'
                            f'\nto be sent with Youtube Alert or Welcome Card',

                color=0x005aef,
            )
            await view.message.edit(embed=emd, view=None)


def setup(bot):
    bot.add_cog(Help(bot))
