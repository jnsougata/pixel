import discord.errors
from discord.ext import commands


class Handlers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        user = ctx.author
        if isinstance(error, commands.MissingRequiredArgument):
            emo = '<:Question:863155023391358987>'
            await ctx.send(
                f'{emo} '
                f'{user.mention} **Please try again with required argument(s)**',
                delete_after=10
            )

        elif isinstance(error, commands.CommandNotFound):
            emo = '<:Faq:862729604666228738>'
            await ctx.send(
                f'{emo} '
                f'{user.mention} **Command not found. '
                f'Use `@{ctx.guild.me.display_name} help` for all commands**',
                delete_after=10
            )

        elif isinstance(error, commands.MissingPermissions):
            emo = '<:mod:878511996184694804>'
            await ctx.send(
                f"{emo} "
                f"{ctx.author.mention} **you are not an administrator**",
                delete_after=10
            )

        elif isinstance(error, commands.CommandOnCooldown):
            seconds = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.send(
                f'{user.mention} command is on cooldown for you!'
                f'\nRetry after **{round(seconds)}s**',
                delete_after=10
            )

        elif isinstance(error, commands.BotMissingPermissions):
            try:
                await ctx.send(
                    f'{user.mention} **I don\'t have enough permission to do it!**',
                    delete_after=10
                )
            except discord.errors.Forbidden:
                pass
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                f'{user.mention} **Only owner can use this command for now!**',
                delete_after=10
            )
        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.send(f'{error}')





def setup(bot):
    bot.add_cog(Handlers(bot))
