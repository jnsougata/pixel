from discord.ext import commands


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['block'])
    @commands.is_owner()
    async def check_(self, ctx: commands.Context):
        """Not Implemented"""
        pass


def setup(bot):
    bot.add_cog(Owner(bot))
