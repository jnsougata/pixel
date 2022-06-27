import disfix
import discord
from bot.extras.emojis import Emo
from bot.views.custom_view import sub_view_msg
from bot.views.youtube_view import sub_view_youtube
from bot.views.welcomer_view import sub_view_welcomer
from bot.views.pingrole_view import sub_view_pingrole


class Setup(disfix.cog):
    def __init__(self, bot: disfix.Bot):
        self.bot = bot

    @disfix.cog.command(
        name='setup',
        description='setup the server configurations',
        dm_access=False,
        category=disfix.CommandType.SLASH
    )
    @disfix.cog.default_permission(discord.Permissions.manage_guild)
    async def setup_command(self, ctx: disfix.Context):
        pass

    @setup_command.subcommand(
        name='youtube',
        description='integrates youtube channel to the server',
        options=[
            disfix.StrOption(
                name='channel',
                description='url or id of the youtube channel',
                required=True),
            disfix.ChannelOption(
                name='receiver',
                description='text channel to receive notifications',
                channel_types=[disfix.ChannelType.GUILD_TEXT, disfix.ChannelType.GUILD_NEWS],
                required=True),
        ]
    )
    async def youtube_command(self, ctx: disfix.Context, channel: str, receiver: discord.TextChannel):
        await ctx.defer()
        await sub_view_youtube(self.bot, ctx, channel, receiver)

    @setup_command.subcommand(
        name='welcomer',
        description='adds welcome card to the server',
        options=[
            disfix.ChannelOption(
                name='channel',
                description='text channel to greet with welcome cards',
                channel_types=[disfix.ChannelType.GUILD_TEXT, disfix.ChannelType.GUILD_NEWS],
                required=True
            ),
            disfix.AttachmentOption(
                name='image',
                description='image file to send when new member joins',
                required=False
            ),
        ]
    )
    async def welcomer_command(self, ctx: disfix.Context, channel: discord.TextChannel, image: discord.Attachment):
        await ctx.defer()
        await sub_view_welcomer(self.bot, ctx, image, channel)

    @setup_command.subcommand(
        name='ping_role',
        description='adds role to ping with youtube notification',
        options=[
            disfix.RoleOption(
                name='role', description='role to ping with youtube notification', required=True),
        ]
    )
    async def ping_role_command(self, ctx: disfix.Context, role: discord.Role):
        await ctx.defer()
        await sub_view_pingrole(self.bot, ctx, role)

    @setup_command.subcommand(
        name='custom_message',
        description='adds custom welcome and notification message',
        options=[
            disfix.IntOption(
                name='option',
                description='type of message to add or edit',
                choices=[
                    disfix.Choice(name='upload', value=1),
                    disfix.Choice(name='welcome', value=0),
                    disfix.Choice(name='livestream', value=2),
                ],
                required=True),
        ]
    )
    async def custom_message_command(self, ctx: disfix.Context, option: int):
        await sub_view_msg(self.bot, ctx, option)


async def setup(bot: disfix.Bot):
    await bot.add_application_cog(Setup(bot))
