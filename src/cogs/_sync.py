from discord.ext import commands
from src.extras.func import db_fetch_object, drive


class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sync")
    @commands.is_owner()
    async def pixel_sync(self, ctx: commands.Context):
        await self.bot.wait_until_ready()
        await ctx.send("Syncing...")
        for guild in self.bot.guilds:
            raw = await db_fetch_object(guild_id=guild.id, key='cover')
            if raw and raw[0].startswith('http'):
                path = f'covers/{guild.id}_card.png'
                try:
                    drive.upload_from_url(url=raw[0], file_name=path)
                except Exception:
                    pass
                finally:
                    await ctx.send(f"Synced {guild.name}'s cover: {raw[0]}")
        await ctx.send("Done!")


def setup(bot: commands.Bot):
    bot.add_cog(Sync(bot))
