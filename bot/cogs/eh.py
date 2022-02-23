import discord
import app_util
import traceback
from typing import Any
from bot.extras.emojis import Emo


class ErrorHandler(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.listener
    async def on_command_error(self, ctx: app_util.Context, error: Exception):
        phrase = 'Something went wrong, please try again... 😔'
        await ctx.send_followup(phrase, ephemeral=True)
        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        stack.insert(0, f'**Guild: {ctx.guild.name} | ID: {ctx.guild.id}**\n')
        tb = ''.join(stack)
        await logger.send(f'```py\n{tb}\n```')


def setup(bot: app_util.Bot):
    bot.add_application_cog(ErrorHandler(bot))
