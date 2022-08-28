import neocord
import discord
from views.config_view import sub_view_config
from views.removal_view import sub_view_remove


class More(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    @neocord.cog.command(name='more', description='remove or view previously set options', dm_access=False)
    async def more(self, ctx: neocord.Context):
        pass

    @more.subcommand(name='remove', description='removes old configuration', options=[
        neocord.IntOption(
            name='option', description='removes a specific option', required=True,
            choices=[
                neocord.Choice('youtube', 1),
                neocord.Choice('welcomer', 2),
                neocord.Choice('ping_role', 3),
                neocord.Choice('custom_message', 4)
            ]
        )
    ])
    async def remove_command(self, ctx: neocord.Context, option: int):
        await ctx.defer()
        await sub_view_remove(self.bot, ctx, option)

    @more.subcommand(name='overview', description='shows any current settings', options=[
        neocord.IntOption(
            name='option', description='removes a specific option', required=True,
            choices=[
                neocord.Choice('youtube', 1),
                neocord.Choice('welcomer', 2),
                neocord.Choice('ping_role', 3),
                neocord.Choice('custom_message', 4)
            ]
        )
    ])
    async def overview(self, ctx: neocord.Context, option: int):
        await ctx.defer()
        await sub_view_config(self.bot, ctx, option)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(More(bot))
