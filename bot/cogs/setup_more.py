import discord
import extlib
from bot.extras.emojis import Emo
from bot.views.config_view import sub_view_config
from bot.views.removal_view import sub_view_remove


async def check(ctx: extlib.Context):

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to `embed links` `use external emojis`')
    else:
        return True


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
    @extlib.cog.check(check)
    async def more_command(self, ctx: extlib.Context, *, remove_option: int, overview_option: int):
        ...

    @more_command.subcommand(
        name='remove',
        description='removes old configuration',
        options=[
            extlib.IntOption(
                name='option', description='removes a specific option',
                choices=[
                    extlib.Choice(name='youtube', value=0),
                    extlib.Choice(name='welcomer', value=2),
                    extlib.Choice(name='ping_role', value=3),
                    extlib.Choice(name='welcome_card', value=4),
                    extlib.Choice(name='custom_message', value=5)
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
                    extlib.Choice(name='youtube', value=0),
                    extlib.Choice(name='welcomer', value=2),
                    extlib.Choice(name='ping_role', value=3),
                    extlib.Choice(name='custom_message', value=5)
                ],
                required=True)
        ]
    )
    async def overview_command(self, ctx: extlib.Context, option: int):
        await ctx.defer()
        await sub_view_config(self.bot, ctx, option)


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(More(bot))
