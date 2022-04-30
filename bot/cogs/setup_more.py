import discord
import app_util
from bot.extras.emojis import Emo
from bot.views.config_view import sub_view_config
from bot.views.removal_view import sub_view_remove


async def check(ctx: app_util.Context):

    p = ctx.channel.permissions_for(ctx.me)

    if not ctx.guild:
        await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
    elif not ctx.author.guild_permissions.manage_guild:
        await ctx.send_response('> 👀  You are not an **Admin** or **Equivalent**')
    elif not p.send_messages and p.embed_links and p.attach_files and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    elif not ctx.options:
        await ctx.send_response('> 👀  you must select **at least one option**')
    elif len(ctx.options) > 1:
        await ctx.send_response('> 👀  please use only **one option at a time**')
    else:
        return True


class More(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='ping',
            description='shows the avg latency of the bot',
        ),
        guild_id=877399405056102431
    )
    async def ping_command(self, ctx: app_util.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='more',
            description='remove or view previously set options',
            options=[
                app_util.IntOption(
                    name='remove', description='remove any old configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),
                app_util.IntOption(
                    name='overview', description='overview of existing configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),
            ],
            required_permission=discord.Permissions.manage_guild
        ),
    )
    @app_util.Cog.before_invoke(check_handler=check)
    async def more_command(self, ctx: app_util.Context, *, remove: int, overview: int):

        await ctx.defer()

        if remove is not None:
            await sub_view_remove(self.bot, ctx, remove)
            return

        if overview is not None:
            await sub_view_config(self.bot, ctx, overview)
            return


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(More(bot))
