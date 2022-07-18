import neocord
import discord
from bot.extras.emojis import Emo
from bot.views.config_view import sub_view_config
from bot.views.removal_view import sub_view_remove


class More(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(
        name='ping',
        description='shows the avg latency of the bot',
        guild_id=877399405056102431,
        category=neocord.CommandType.SLASH
    )
    async def ping_command(self, ctx: neocord.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @neocord.cog.command(
        name='simulate',
        description='simulates a message dispatch event',
        guild_id=877399405056102431,
        category=neocord.CommandType.SLASH,
        options=[
            neocord.StrOption(
                name='event',
                description='name of the event to simulate',
                required=True
            )
        ]
    )
    async def simulate_command(self, ctx: neocord.Context, event: str):
        await ctx.send_response(f'**Simulating:** {event}')
        if event.upper() == 'MEMBER_JOIN':
            self.bot.dispatch(event, ctx.author)
        else:
            await ctx.send_followup(f'**Unknown event:** {event}')

    @neocord.cog.command(
        name='more',
        description='remove or view previously set options',
        dm_access=False,
        category=neocord.CommandType.SLASH
    )
    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    async def more_command(self, ctx: neocord.Context):
        pass

    @more_command.subcommand(
        name='remove',
        description='removes old configuration',
        options=[
            neocord.IntOption(
                name='option', description='removes a specific option',
                choices=[
                    neocord.Choice(name='youtube', value=1),
                    neocord.Choice(name='welcomer', value=2),
                    neocord.Choice(name='ping_role', value=3),
                    neocord.Choice(name='custom_message', value=4),
                ],
                required=True),
        ]
    )
    async def remove_command(self, ctx: neocord.Context, option: int):
        await ctx.defer()
        await sub_view_remove(self.bot, ctx, option)

    @more_command.subcommand(
        name='overview',
        description='shows any current settings',
        options=[
            neocord.IntOption(
                name='option', description='overview of existing configuration',
                choices=[
                    neocord.Choice(name='youtube', value=1),
                    neocord.Choice(name='welcomer', value=2),
                    neocord.Choice(name='ping_role', value=3),
                    neocord.Choice(name='custom_message', value=4)
                ],
                required=True)
        ]
    )
    async def overview_command(self, ctx: neocord.Context, option: int):
        await ctx.defer()
        await sub_view_config(self.bot, ctx, option)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(More(bot))
