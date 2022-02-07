import discord
import traceback
from src.extras.emojis import *
from discord.ext import commands
from extslash.commands import ApplicationContext, Bot
from src.iviews.prefix_view import sub_view_prefix
from src.iviews.msg_view import sub_view_msg
from src.iviews.receiver_view import sub_view_receiver
from src.iviews.reception_view import sub_view_reception
from src.iviews.pingrole_view import sub_view_pingrole
from src.iviews.welcome_view import sub_view_welcomecard
from src.iviews.youtube_view import sub_view_youtube


class BaseView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.timeout = 180

    async def on_timeout(self):
        pass


class CommandMenu(discord.ui.Select):

    def __init__(self, ctx: ApplicationContext, bot: Bot):

        self.bot = bot
        self.ctx = ctx

        options = [
            discord.SelectOption(label='\u200b', value='0', emoji=Emo.CROSS),
            discord.SelectOption(label='Prefix', value='1', emoji=Emo.TAG),
            discord.SelectOption(label='YouTube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='Receiver', value='3', emoji=Emo.PING),
            discord.SelectOption(label='Reception', value='4', emoji=Emo.DEAL),
            discord.SelectOption(label='Ping Role', value='5', emoji=Emo.BELL),
            discord.SelectOption(label='Welcome Card', value='6', emoji=Emo.IMG),
            discord.SelectOption(label='Customize Message', value='7', emoji=Emo.CUSTOM),
        ]

        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
            placeholder='select a command'
        )

    async def callback(self, interaction: discord.Interaction):

        if interaction.user == self.ctx.author:
            try:
                await interaction.response.defer()
                if int(self.values[0]) == 0:
                    await self.ctx.delete_response()
                elif int(self.values[0]) == 1:
                    await sub_view_prefix(self.ctx, self.bot)
                elif int(self.values[0]) == 2:
                    await sub_view_youtube(self.ctx, self.bot)
                elif int(self.values[0]) == 3:
                    await sub_view_receiver(self.ctx, self.bot)
                elif int(self.values[0]) == 4:
                    await sub_view_reception(self.ctx, self.bot)
                elif int(self.values[0]) == 5:
                    await sub_view_pingrole(self.ctx, self.bot)
                elif int(self.values[0]) == 6:
                    await sub_view_welcomecard(self.ctx, self.bot)
                elif int(self.values[0]) == 7:
                    await sub_view_msg(self.ctx, self.bot)
            except Exception as e:
                if isinstance(e, discord.errors.NotFound):
                    pass
                else:
                    logger = self.bot.get_channel(938059433794240523)
                    tb = traceback.format_exception(type(e), e, e.__traceback__)
                    await logger.send(f'```py\n{tb}\n```')
        else:
            await interaction.response.send_message('You are not allowed to control this message!', ephemeral=True)