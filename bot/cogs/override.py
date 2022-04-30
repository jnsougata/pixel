import discord
import app_util
from aiotube import Channel
from bot.extras.emojis import Emo


async def check(ctx: app_util.Context):

    p = ctx.channel.permissions_for(ctx.me)

    if not ctx.guild:
        await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
    elif not ctx.author.guild_permissions.manage_guild:
        await ctx.send_response('> 👀  You are not an **Admin** or **Server Manager**')
    elif not p.send_messages and p.embed_links and p.attach_files and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    elif not ctx.options:
        await ctx.send_response('> 👀  you must select at least one option')
    else:
        return True


class Override(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.before_invoke(check_handler=check)
    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='force',
            description='forces to check for new videos',
            options=[app_util.StrOption(name='url', description='youtube channel url to check', required=True)]
        ),
    )
    async def force_check(self, ctx: app_util.Context, url: str):
        await ctx.send_response(f'> Command is under development...')


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Override(bot))
