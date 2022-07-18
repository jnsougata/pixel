import neocord
import discord
from bot.extras.emojis import Emo
from bot.views.custom_view import sub_view_msg
from bot.views.youtube_view import sub_view_youtube
from bot.views.welcomer_view import sub_view_welcomer
from bot.views.pingrole_view import sub_view_pingrole


class Setup(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(
        name='setup',
        description='setup the server configurations',
        dm_access=False,
        category=neocord.CommandType.SLASH
    )
    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    async def setup_command(self, ctx: neocord.Context):
        pass

    @setup_command.subcommand(
        name='youtube',
        description='integrates youtube channel to the server',
        options=[
            neocord.StrOption(
                name='channel',
                description='url or id of the youtube channel',
                required=True),
            neocord.ChannelOption(
                name='receiver',
                description='text channel to receive notifications',
                channel_types=[neocord.ChannelType.GUILD_TEXT, neocord.ChannelType.GUILD_NEWS],
                required=True),
        ]
    )
    async def youtube_command(self, ctx: neocord.Context, channel: str, receiver: discord.TextChannel):
        await ctx.defer()
        await sub_view_youtube(self.bot, ctx, channel, receiver)

    @setup_command.subcommand(
        name='welcomer',
        description='adds welcome card to the server',
        options=[
            neocord.ChannelOption(
                name='channel',
                description='text channel to greet with welcome cards',
                channel_types=[neocord.ChannelType.GUILD_TEXT, neocord.ChannelType.GUILD_NEWS],
                required=True
            ),
            neocord.AttachmentOption(
                name='image',
                description='image file to send when new member joins',
                required=False
            ),
        ]
    )
    async def welcomer_command(self, ctx: neocord.Context, channel: discord.TextChannel, image: discord.Attachment):
        await ctx.defer()
        await sub_view_welcomer(self.bot, ctx, image, channel)

    @setup_command.subcommand(
        name='ping_role',
        description='adds role to ping with youtube notification',
        options=[
            neocord.RoleOption(
                name='role', description='role to ping with youtube notification', required=True),
        ]
    )
    async def ping_role_command(self, ctx: neocord.Context, role: discord.Role):
        await ctx.defer()
        await sub_view_pingrole(self.bot, ctx, role)

    @setup_command.subcommand(
        name='custom_message',
        description='adds custom welcome and notification message',
        options=[
            neocord.IntOption(
                name='option',
                description='type of message to add or edit',
                choices=[
                    neocord.Choice(name='upload', value=1),
                    neocord.Choice(name='welcome', value=0),
                    neocord.Choice(name='livestream', value=2),
                ],
                required=True),
        ]
    )
    async def custom_message_command(self, ctx: neocord.Context, option: int):
        await sub_view_msg(self.bot, ctx, option)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Setup(bot))
