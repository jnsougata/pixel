import discord.errors
from discord.ext import commands
from src.extras.func import prefix_fetcher


class Handlers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        p = await prefix_fetcher(ctx.guild.id)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f'Please try again with required **argument(s)**',
                delete_after=15
            )
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                content=f"You are not an **`ADMIN`**",
                delete_after=10
            )
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.reply(
                f'This command is on cooldown for you!'
                f'\nRetry after **{round(seconds)}s**',
                delete_after=15
            )
        elif isinstance(error, commands.BotMissingPermissions):
            try:
                await ctx.reply(
                    f'**I don\'t have enough permission to do it!**',
                    delete_after=15
                )
            except discord.errors.Forbidden:
                pass
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                f'Only **Zen#8080** can use this command!',
                delete_after=15
            )
        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.reply(
                content='Something weird happened. Devs will fix it soon!'
            )
            print(f'{error.__cause__}')


def setup(bot):
    bot.add_cog(Handlers(bot))
