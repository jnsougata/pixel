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

        button = discord.ui.Button(
            label='DEV SERVER',
            url='https://discord.gg/VE5qRFfmG2',
            style=discord.ButtonStyle.link)

        embed = discord.Embed(
            description=f'(**!**) Something went wrong'
                        f'\n\n{Emo.STAFF}  Developer will be fixing it soon'
                        f'\n\n{Emo.SUP}  You can also join the development server'
                        f'\nto get more information and share your feedback!',
            color=discord.Color.red()
        )
        view = discord.ui.View()
        view.add_item(button)
        await ctx.send_followup(embed=embed, view=view, ephemeral=True)
        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        if len(tb) < 4096:
            await logger.send(embed=discord.Embed(
                description=f'**Guild: {ctx.guild.name} | ID: {ctx.guild.id}**\n```py\n{tb}\n```'))
        else:
            print(f'**Guild: {ctx.guild.name} | ID: {ctx.guild.id}**\n```py\n{tb}\n```')
            await logger.send(embed=discord.Embed(
                description=f'**Guild: {ctx.guild.name} | ID: {ctx.guild.id}**\n```py\n{tb[:4096]}\n```'))


def setup(bot: app_util.Bot):
    bot.add_application_cog(ErrorHandler(bot))
