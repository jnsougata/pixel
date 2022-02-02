import discord
from src.extras.emojis import *
from discord.ext import commands
from src.views.aux_view import BaseView, CommandMenu


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['settings', 'setup'])
    async def settings_(self, ctx: commands.Context):
        emd = discord.Embed(title=f'{Emo.SETUP} use menu below to setup', colour=0x005aef)
        emd.set_footer(text=f'⏱️ this menu will disappear after 3 minutes')
        view = BaseView()
        view.add_item(CommandMenu(ctx, self.bot))
        view.message = await ctx.send(embed=emd, view=view)


def setup(bot):
    bot.add_cog(Settings(bot))
