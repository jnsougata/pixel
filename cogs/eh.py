import discord
import neocord
import traceback
from extras.emojis import Emo


class ErrorHandler(neocord.cog):

    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.listener
    async def on_app_command_error(self, ctx: neocord.Context, error: Exception):

        button = discord.ui.Button(
            label='DEV SERVER',
            url='https://discord.gg/VE5qRFfmG2',
            style=discord.ButtonStyle.link)

        embed = discord.Embed(
            description=f'(**!**) Something went wrong'
                        f'\n\n{Emo.STAFF} Developer will be fixing it soon'
                        f'\n\n{Emo.DISCORD} You can also join the development server'
                        f'\nto get more information and share your feedback!',
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        view = discord.ui.View()
        view.add_item(button)
        if not ctx.responded:
            await ctx.send_response(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.send_followup(embed=embed, view=view)
        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        if len(tb) < 4096:
            await logger.send(embed=discord.Embed(
                title='Something Unexpected Occurred...',
                description=f'```py'
                            f'\n{ctx.guild.name}'
                            f'\n-------------------------------'
                            f'\ncommand_name = {ctx.name}'
                            f'\nguild_id = {ctx.guild.id}'
                            f'\n-------------------------------\n{tb}\n```')
            )
        else:
            await logger.send(embed=discord.Embed(
                title='Something Unexpected Occurred...',
                description=f'```py'
                            f'\n{ctx.guild.name}'
                            f'\n-------------------------------'
                            f'\ncommand_name = {ctx.name}'
                            f'\nguild_id = {ctx.guild.id}'
                            f'\n-------------------------------\n{tb[:4000]}\n```')
            )
            print(f'**Guild: {ctx.guild.name} | ID: {ctx.guild.id}**\n```py\n{tb}\n```')


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(ErrorHandler(bot))
