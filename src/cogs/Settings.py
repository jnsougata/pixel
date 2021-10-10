import discord
from src.extras.emojis import *
from discord.ext import commands
from src.views.subPrefix import sub_view_prefix
from src.views.subReceiver import sub_view_receiver




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
            self.clear_items()
            await self.message.edit(view=self)
        except discord.errors.NotFound:
            return



class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.message = None

        super().__init__()
        self.value = None


    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
            self.stop()





class BaseMenu(discord.ui.Select):

    def __init__(self, context: commands.Context, bot:discord.Client):

        self.ctx = context
        self.bot = bot

        options = [
            discord.SelectOption(label='prefix', value='0', emoji=Emo.TAG),
            discord.SelectOption(label='receiver', value='1', emoji=Emo.PING),
            discord.SelectOption(label='youtube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='reception', value='3', emoji=Emo.DEAL),
            discord.SelectOption(label='welcomecard', value='4', emoji=Emo.IMG),
        ]

        super().__init__(
            placeholder='Select a command',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if interaction.user == self.ctx.author:

            if int(self.values[0]) == 0:

                await sub_view_prefix(
                    ctx = self.ctx,
                    interaction = interaction,
                    bot = self.bot
                )

            elif int(self.values[0]) == 1:

                await sub_view_receiver(
                    ctx=self.ctx,
                    interaction=interaction,
                    bot=self.bot
                )

            else:
                await self.ctx.send('Work in progress!')

















        else:
            await interaction.response.send_message(
                'You are not allowed to control this message!', ephemeral=True
            )




class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator = True)
    @commands.command(aliases = ['settings', 'setup', 's'])
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