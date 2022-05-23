import discord
import app_util
from bot.extras.emojis import Emo
from bot.views.config_view import sub_view_config
from bot.views.removal_view import sub_view_remove


async def check(ctx: app_util.Context):

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to `embed links` `use external emojis`')
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
            dm_access=False,
            options=[
                app_util.SubCommand(
                    name='remove', description='removes old configuration',
                    options=[
                        app_util.IntOption(
                            name='option', description='removes a specific option',
                            choices=[
                                app_util.Choice(name='youtube', value=0),
                                app_util.Choice(name='welcomer', value=2),
                                app_util.Choice(name='ping_role', value=3),
                                app_util.Choice(name='welcome_card', value=4),
                                app_util.Choice(name='custom_message', value=5)
                            ],
                            required=True),
                    ]
                ),
                app_util.SubCommand(
                    name='overview', description='shows any current settings',
                    options=[
                        app_util.IntOption(
                            name='option', description='overview of existing configuration',
                            choices=[
                                app_util.Choice(name='youtube', value=0),
                                app_util.Choice(name='welcomer', value=2),
                                app_util.Choice(name='ping_role', value=3),
                                app_util.Choice(name='custom_message', value=5)
                            ],
                            required=True)
                    ]
                ),
            ],
        ),
    )
    @app_util.Cog.default_permission(discord.Permissions.manage_guild)
    @app_util.Cog.check(check)
    async def more_command(self, ctx: app_util.Context, *, remove_option: int, overview_option: int):
        await ctx.defer()
        if remove_option is not None:
            await sub_view_remove(self.bot, ctx, remove_option)
            return
        if overview_option is not None:
            await sub_view_config(self.bot, ctx, overview_option)
            return


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(More(bot))
