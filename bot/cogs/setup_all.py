import discord
import extlib
from bot.extras.emojis import Emo
from bot.views.custom_view import sub_view_msg
from bot.views.youtube_view import sub_view_youtube
from bot.views.welcomer_view import sub_view_welcomer
from bot.views.pingrole_view import sub_view_pingrole


async def check(ctx: extlib.Context):

    if not ctx.channel:
        await ctx.send_response('> 😓  command can not be used inside `threads`')
        return False

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to `embed links` `use external emojis`')
    else:
        return True


class Setup(extlib.cog):
    def __init__(self, bot: extlib.Bot):
        self.bot = bot

    @extlib.cog.command(
        name='setup',
        description='setup the server configurations',
        dm_access=False,
        category=extlib.CommandType.SLASH
    )
    @extlib.cog.default_permission(discord.Permissions.manage_guild)
    @extlib.cog.check(check)
    async def setup_command(self, ctx: extlib.Context):
        pass

    @setup_command.subcommand(
        name='youtube',
        description='integrates youtube channel to the server',
        options=[
            extlib.StrOption(
                name='channel',
                description='url or id of the youtube channel',
                required=True),
            extlib.ChannelOption(
                name='receiver',
                description='text channel to receive notifications',
                channel_types=[extlib.ChannelType.GUILD_TEXT, extlib.ChannelType.GUILD_NEWS],
                required=True),
        ]
    )
    async def youtube_command(self, ctx: extlib.Context, channel: str, receiver: discord.TextChannel):
        await ctx.defer()
        await sub_view_youtube(self.bot, ctx, channel, receiver)

    @setup_command.subcommand(
        name='welcomer',
        description='adds welcome card to the server',
        options=[
            extlib.ChannelOption(
                name='channel',
                description='text channel to greet with welcome cards',
                channel_types=[extlib.ChannelType.GUILD_TEXT, extlib.ChannelType.GUILD_NEWS],
                required=True
            ),
            extlib.AttachmentOption(
                name='image',
                description='image file to send when new member joins',
                required=False
            ),
        ]
    )
    async def welcomer_command(self, ctx: extlib.Context, channel: discord.TextChannel, image: discord.Attachment):
        await ctx.defer()
        await sub_view_welcomer(self.bot, ctx, image, channel)

    @setup_command.subcommand(
        name='ping_role',
        description='adds role to ping with youtube notification',
        options=[
            extlib.RoleOption(
                name='role', description='role to ping with youtube notification', required=True),
        ]
    )
    async def ping_role_command(self, ctx: extlib.Context, role: discord.Role):
        await ctx.defer()
        await sub_view_pingrole(self.bot, ctx, role)

    @setup_command.subcommand(
        name='custom_message',
        description='adds custom welcome and notification message',
        options=[
            extlib.IntOption(
                name='option',
                description='type of message to add or edit',
                choices=[
                    extlib.Choice(name='upload', value=1),
                    extlib.Choice(name='welcome', value=0),
                    extlib.Choice(name='livestream', value=2),
                ],
                required=True),
        ]
    )
    async def custom_message_command(self, ctx: extlib.Context, option: int):
        await sub_view_msg(self.bot, ctx, option)


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(Setup(bot))
