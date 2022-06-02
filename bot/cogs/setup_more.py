import discord
import extlib
from bot.extras.emojis import Emo
from bot.views.config_view import sub_view_config
from bot.views.removal_view import sub_view_remove


class More(extlib.cog):
    def __init__(self, bot: extlib.Bot):
        self.bot = bot

    @extlib.cog.command(
        name='ping',
        description='shows the avg latency of the bot',
        guild_id=877399405056102431,
        category=extlib.CommandType.SLASH
    )
    async def ping_command(self, ctx: extlib.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @extlib.cog.command(
        name='more',
        description='remove or view previously set options',
        dm_access=False,
        category=extlib.CommandType.SLASH
    )
    @extlib.cog.default_permission(discord.Permissions.manage_guild)
    async def more_command(self, ctx: extlib.Context):
        pass

    @more_command.subcommand(
        name='remove',
        description='removes old configuration',
        options=[
            extlib.IntOption(
                name='option', description='removes a specific option',
                choices=[
                    extlib.Choice(name='youtube', value=1),
                    extlib.Choice(name='welcomer', value=2),
                    extlib.Choice(name='ping_role', value=3),
                    extlib.Choice(name='custom_message', value=4),
                ],
                required=True),
        ]
    )
    async def remove_command(self, ctx: extlib.Context, option: int):
        await ctx.defer()
        await sub_view_remove(self.bot, ctx, option)

    @more_command.subcommand(
        name='overview',
        description='shows any current settings',
        options=[
            extlib.IntOption(
                name='option', description='overview of existing configuration',
                choices=[
                    extlib.Choice(name='youtube', value=1),
                    extlib.Choice(name='welcomer', value=2),
                    extlib.Choice(name='ping_role', value=3),
                    extlib.Choice(name='custom_message', value=4)
                ],
                required=True)
        ]
    )
    async def overview_command(self, ctx: extlib.Context, option: int):
        await ctx.defer()
        await sub_view_config(self.bot, ctx, option)


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(More(bot))
