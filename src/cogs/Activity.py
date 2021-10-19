import discord
from discord.ext import commands, tasks

class ActivityHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.Activity.start()


    @tasks.loop(hours=12)
    async def Activity(self):
        await self.bot.wait_until_ready()
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f'.help | .setup'
        )
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=activity
        )




def setup(bot):
    bot.add_cog(ActivityHandler(bot))