import discord
from src.extras.emojis import *
from discord.ext import commands
from src.views.subARole import sub_view_arole
from src.views.subPrefix import sub_view_prefix
from src.views.subYouTube import sub_view_youtube
from src.views.subStreamer import sub_view_streamer
from src.views.subReceiver import sub_view_receiver
from src.views.subReception import sub_view_reception
from src.views.subJoincard import sub_view_welcomecard


class BaseView(discord.ui.View):
    def __init__(
            self,
            message: discord.Message = None,
    ):
        self.message = message
        super().__init__()
        self.value = None
        self.timeout = 30

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except (discord.errors.NotFound, discord.errors.Forbidden):
            pass


class BaseMenu(discord.ui.Select):

    def __init__(self, context: commands.Context, bot: discord.Client):

        self.bot = bot
        self.ctx = context

        options = [
            discord.SelectOption(label='​', value='100', emoji=Emo.CROSS),
            discord.SelectOption(label='Prefix', value='0', emoji=Emo.TAG),
            discord.SelectOption(label='YouTube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='Receiver', value='1', emoji=Emo.PING),
            discord.SelectOption(label='Reception', value='3', emoji=Emo.DEAL),
            discord.SelectOption(label='Welcome Card', value='4', emoji=Emo.IMG),
            # discord.SelectOption(label='Alert Role (BETA)', value='5', emoji=Emo.BELL),
            # discord.SelectOption(label='Manage Streamer (BETA)', value='6', emoji=Emo.STREAMER)
        ]

        super().__init__(
            placeholder='Select a command',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) == 100:
                try:
                    await interaction.message.delete()
                except discord.errors.NotFound:
                    pass
            if int(self.values[0]) == 0:
                await sub_view_prefix(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 1:
                await sub_view_receiver(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 2:
                await sub_view_youtube(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 3:
                await sub_view_reception(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 4:
                await sub_view_welcomecard(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 5:
                await sub_view_arole(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            elif int(self.values[0]) == 6:
                await sub_view_streamer(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )
            else:
                pass
        else:
            await interaction.response.send_message(
                'You are not allowed to control this message!', ephemeral=True
            )


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['settings', 'setup'])
    async def settings_(self, ctx: commands.Context):
        emd = discord.Embed(
            description='\nChoose any command form menu to use:',
            colour=0x005aef
        )
        emd.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url
        )
        view = BaseView()
        view.add_item(BaseMenu(context=ctx, bot=self.bot))
        view.message = await ctx.send(embed=emd, view=view)


def setup(bot):
    bot.add_cog(Settings(bot))
