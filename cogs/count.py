import os
import topgg
import logging
from discord.ext import commands, tasks


class ServerCounter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.counter.start()

    @tasks.loop(minutes=30)
    async def counter(self):
        await self.bot.wait_until_ready()
        dbl_token = os.getenv('DBL_TOKEN')
        if dbl_token:
            self.bot.topggpy = topgg.DBLClient(self.bot, os.getenv('DBL_TOKEN'))
            try:
                await self.bot.topggpy.post_guild_count()
                logging.info(f" [PID: N/A] Posted Server Count: {self.bot.topggpy.guild_count} ]")
                await self.bot.topggpy.close()
            except Exception as e:
                print(f"Failed to post server count\n{e.__class__.__name__}:\n{e}")
            finally:
                await self.bot.topggpy.close()


async def setup(bot):
    await bot.add_cog(ServerCounter(bot))
