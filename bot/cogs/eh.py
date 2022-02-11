import traceback
import discord.errors
from discord.ext import commands


class EH(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f'Please try again with required **argument(s)**',
                delete_after=15
            )

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(content=f"You are not an **Admin** or **Equivalent**")

        elif isinstance(error, commands.CommandOnCooldown):
            seconds = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.reply(
                f'This command is on cooldown for you!'
                f'\nRetry after **{round(seconds)}s**',
                delete_after=15
            )

        elif isinstance(error, commands.BotMissingPermissions):
            try:
                await ctx.reply(f'**I don\'t have enough permission to do it here!**')
            except discord.errors.Forbidden:
                pass

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f'Only **Owner** can use this command!')

        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.errors.Forbidden):
                try:
                    await ctx.reply(
                        'Please make sure here I have permissions to send `embeds` `buttons` `emojis` `attachments`')
                except discord.errors.Forbidden:
                    return
            elif isinstance(error.original, discord.errors.NotFound):
                return
            else:
                try:
                    await ctx.reply(content='Something weird happened. Devs will fix it soon!')
                except discord.errors.Forbidden:
                    pass
                finally:
                    stack = traceback.format_exception(type(error), error, error.__traceback__)
                    tb = ''.join(stack)
                    debug_channel = self.bot.get_channel(938059433794240523)
                    await debug_channel.send(f'```py\n{tb}\n```')
        else:
            stack = traceback.format_exception(type(error), error, error.__traceback__)
            tb = ''.join(stack)
            debug_channel = self.bot.get_channel(938059433794240523)
            await debug_channel.send(f'```py\n{tb}\n```')


def setup(bot):
    bot.add_cog(EH(bot))
