import discord
from typing import Union
from src.extras.emojis import *
from discord.ext import commands
from extslash.commands import ApplicationContext
from src.views.roleping_view import sub_view_rping
from src.views.youtube_view import sub_view_youtube
from src.views.receiver_view import sub_view_receiver
from src.views.reception_view import sub_view_reception
from src.views.welcome_view import sub_view_welcomecard


class BaseView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.timeout = 180
        self.value = None
        self.message = None

    async def on_timeout(self):
        try:
            await self.message.delete()
        except Exception:
            return


class CommandMenu(discord.ui.Select):

    def __init__(self, ctx: Union[commands.Context, ApplicationContext], bot: discord.Client):

        self.bot = bot
        self.ctx = ctx

        options = [
            discord.SelectOption(label='\u200b', value='100', emoji=Emo.CROSS),
            discord.SelectOption(label='YouTube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='Receiver', value='1', emoji=Emo.PING),
            discord.SelectOption(label='Reception', value='3', emoji=Emo.DEAL),
            discord.SelectOption(label='Ping role', value='5', emoji=Emo.BELL),
            discord.SelectOption(label='Welcome card', value='4', emoji=Emo.IMG),
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
                
                if int(self.values[0]) == 1:
                    await sub_view_receiver(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 2:
                    await sub_view_youtube(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 3:
                    await sub_view_reception(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 4:
                    await sub_view_welcomecard(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 5:
                    await sub_view_rping(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 6:
                    await sub_view_streamer(ctx=self.ctx, interaction=interaction, bot=self.bot)

                elif int(self.values[0]) == 100:
                    try:
                        await interaction.message.delete()
                    except discord.errors.NotFound:
                        pass
                else:
                    pass

            except discord.errors.Forbidden:
                await self.ctx.send(
                    f'\n{self.ctx.author.mention} '
                    f'I don\'t have enough permission to send `embeds` `views` `buttons` `emojis` `attachments`',
                    delete_after=30)
        else:
            await interaction.response.send_message('You are not allowed to control this message!', ephemeral=True)
