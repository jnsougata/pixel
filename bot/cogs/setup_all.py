import discord
import traceback
import app_util
from bot.extras.emojis import Emo
from bot.views.msg_view import sub_view_msg
from bot.views.youtube_view import sub_view_youtube
from bot.views.receiver_view import sub_view_receiver
from bot.views.pingrole_view import sub_view_pingrole
from bot.views.reception_view import sub_view_reception
from bot.views.welcome_view import sub_view_welcomecard


async def check(ctx: app_util.Context):

    def check():
        p = ctx.channel.permissions_for(ctx.me)
        return p.send_messages and p.embed_links and p.attach_files and p.external_emojis

    if not ctx.guild:
        await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
    elif not ctx.author.guild_permissions.manage_guild:
        await ctx.send_response('> 👀  You are not an **Admin** or **Server Manager**')
    elif not check():
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    elif not ctx.options:
        await ctx.send_response('> 👀  you must select **at least one option**')
    elif len(ctx.options) > 1:
        await ctx.send_response('> 👀  please use only **one option at a time**')
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
            description='configure PixeL for your server',
            options=[
                app_util.StrOption(
                    name='youtube',
                    description='type any youtube channel by url or id',
                    required=False),

                app_util.ChannelOption(
                    name='receiver',
                    description='text channel to receive youtube videos',
                    channel_types=[
                        app_util.DiscordChannelType.GUILD_TEXT,
                        app_util.DiscordChannelType.GUILD_NEWS],
                    required=False),

                app_util.ChannelOption(
                    name='reception',
                    description='text channel to receive welcome cards',
                    channel_types=[
                        app_util.DiscordChannelType.GUILD_TEXT,
                        app_util.DiscordChannelType.GUILD_NEWS],
                    required=False),

                app_util.RoleOption(
                    name='ping_role',
                    description='role to ping with youtube notification',
                    required=False),

                app_util.AttachmentOption(
                    name='welcome_card',
                    description='image file to send when new member joins',
                    required=False),

                app_util.IntOption(
                    name='custom_message',
                    description='custom welcome and notification message',
                    choices=[
                        app_util.Choice(name='upload_message', value=1),
                        app_util.Choice(name='welcome_message', value=0),
                        app_util.Choice(name='livestream_message', value=2),
                    ],
                    required=False),
            ],
        )
    )
    @app_util.Cog.before_invoke(check=check)
    async def setup_command(
            self, ctx: app_util.Context,
            *,
            youtube: str, ping_role: discord.Role, receiver: discord.TextChannel,
            reception: discord.TextChannel, welcome_card: discord.Attachment, custom_message: int):

        if youtube:
            await ctx.defer()
            await sub_view_youtube(ctx, youtube)
            return
        if receiver:
            await ctx.defer()
            await sub_view_receiver(ctx, receiver)
            return
        if reception:
            await ctx.defer()
            await sub_view_reception(ctx, reception)
            return
        if ping_role:
            await ctx.defer()
            await sub_view_pingrole(ctx, ping_role)
            return
        if welcome_card:
            await ctx.defer()
            await sub_view_welcomecard(ctx, welcome_card.url)
            return
        if custom_message is not None:
            await sub_view_msg(ctx, custom_message, self.bot)
            return


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Setup(bot))
