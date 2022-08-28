import neocord
import discord
from views.custom_view import sub_view_msg
from views.youtube_view import sub_view_youtube
from views.welcomer_view import sub_view_welcomer
from views.pingrole_view import sub_view_pingrole


class Setup(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    @neocord.cog.command(name='setup', description='setup the server configurations', dm_access=False)
    async def setup(self, ctx: neocord.Context):
        pass

    @setup.subcommand(name='youtube', description='integrates youtube channel to the server', options=[
        neocord.StrOption(
            name='channel', description='url or id of the youtube channel', required=True),
        neocord.ChannelOption(
            name='receiver', description='text channel to receive notifications',
            channel_types=[neocord.ChannelType.GUILD_TEXT, neocord.ChannelType.GUILD_NEWS], required=True)
    ])
    async def youtube(self, ctx: neocord.Context, channel: str, receiver: discord.TextChannel):
        await ctx.defer()
        await sub_view_youtube(self.bot, ctx, channel, receiver)

    @setup.subcommand(name='welcomer', description='adds welcome card to the server', options=[
        neocord.ChannelOption(
            name='channel', description='text channel to greet with welcome cards',
            channel_types=[neocord.ChannelType.GUILD_TEXT, neocord.ChannelType.GUILD_NEWS], required=True),
        neocord.AttachmentOption(
            name='image', description='image file to send when new member joins', required=False)
        ]
    )
    async def welcomer(self, ctx: neocord.Context, channel: discord.TextChannel, image: discord.Attachment):
        await ctx.defer()
        await sub_view_welcomer(self.bot, ctx, image, channel)

    @setup.subcommand(name='ping_role', description='adds role to ping with youtube notification', options=[
        neocord.RoleOption(name='role', description='role to ping with youtube notification', required=True)
    ])
    async def ping_role(self, ctx: neocord.Context, role: discord.Role):
        await ctx.defer()
        await sub_view_pingrole(self.bot, ctx, role)

    @setup.subcommand(name='custom_message', description='adds custom welcome and notification message', options=[
        neocord.IntOption(
            name='option', description='type of message to add or edit', required=True,
            choices=[
                neocord.Choice('upload', 1),
                neocord.Choice('welcome', 0),
                neocord.Choice('livestream', 2),
            ]
        )
    ])
    async def custom_message_command(self, ctx: neocord.Context, option: int):
        await sub_view_msg(self.bot, ctx, option)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Setup(bot))
