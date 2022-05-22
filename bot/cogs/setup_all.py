import discord
import app_util
from bot.extras.emojis import Emo
from bot.views.modal_msg_view import sub_view_msg
from bot.views.youtube_view import sub_view_youtube
from bot.views.welcomer_view import sub_view_welcomer
from bot.views.pingrole_view import sub_view_pingrole


async def check(ctx: app_util.Context):

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.attach_files and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    elif not ctx.options:
        await ctx.send_response('> 👀  you must select **at least one option**')
    else:
        return True


class Setup(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(name='ping', description='shows the avg latency of the bot'),
        guild_id=877399405056102431
    )
    async def ping_command(self, ctx: app_util.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='setup',
            description='setup the server configurations',
            dm_access=False,
            options=[
                app_util.SubCommand(
                    name='youtube', description='integrates youtube channel to the server',
                    options=[
                        app_util.StrOption(
                            name='channel',
                            description='url or id of the youtube channel',
                            required=True),
                        app_util.ChannelOption(
                            name='receiver',
                            description='text channel to receive notifications',
                            channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
                            required=True),
                    ]
                ),
                app_util.SubCommand(
                    name='welcomer', description='adds welcome card to the server',
                    options=[
                        app_util.ChannelOption(
                            name='channel',
                            description='text channel to greet with welcome cards',
                            channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
                            required=True),
                        app_util.AttachmentOption(
                            name='image',
                            description='image file to send when new member joins', required=False),
                    ]
                ),
                app_util.SubCommand(
                    name='ping_role', description='adds role to ping with youtube notification',
                    options=[
                        app_util.RoleOption(
                            name='role', description='role to ping with youtube notification', required=True),
                    ]
                ),
                app_util.SubCommand(
                    name='custom_message',
                    description='adds custom welcome and notification message',
                    options=[
                        app_util.IntOption(
                            name='option',
                            description='type of message to add or edit',
                            choices=[
                                app_util.Choice(name='upload', value=1),
                                app_util.Choice(name='welcome', value=0),
                                app_util.Choice(name='livestream', value=2),
                            ],
                            required=True),
                    ]
                )
            ],
        )
    )
    @app_util.Cog.default_permission(discord.Permissions.manage_guild)
    @app_util.Cog.check(check)
    async def setup_command(
            self, ctx: app_util.Context,
            *,
            youtube: bool, youtube_channel: str, youtube_receiver: discord.TextChannel,
            welcomer: bool, welcomer_channel: discord.TextChannel, welcomer_image: discord.Attachment,
            ping_role: bool, ping_role_role: discord.Role, custom_message: bool, custom_message_option: int
    ):
        if youtube:
            await ctx.defer()
            await sub_view_youtube(self.bot, ctx, youtube_channel, youtube_receiver)
            return
        if ping_role:
            await ctx.defer()
            await sub_view_pingrole(self.bot, ctx, ping_role_role)
            return
        if welcomer:
            await ctx.defer()
            await sub_view_welcomer(self.bot, ctx, welcomer_image, welcomer_channel)
            return
        if custom_message is not None:
            await sub_view_msg(self.bot, ctx, custom_message_option)
            return


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Setup(bot))
