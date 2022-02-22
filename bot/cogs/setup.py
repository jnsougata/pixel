import discord
import traceback
import app_util
from bot.extras.emojis import Emo
from bot.views.msg_view import sub_view_msg
from bot.views.view_config import sub_view_config
from bot.views.youtube_view import sub_view_youtube
from bot.views.remove_config import sub_view_remove
from bot.views.receiver_view import sub_view_receiver
from bot.views.pingrole_view import sub_view_pingrole
from bot.views.reception_view import sub_view_reception
from bot.views.welcome_view import sub_view_welcomecard


class Setup(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='ping',
            description='shows the avg latency of the bot',
        ),
        guild_id=877399405056102431
    )
    async def ping_command(self, ctx: app_util.Context):
        await ctx.defer(ephemeral=True)
        await ctx.send_followup(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='setup',
            description='configure PixeL for your Server',
            options=[
                app_util.IntOption(
                    name='remove',
                    description='remove any old configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),
                app_util.IntOption(
                    name='overview',
                    description='overview of existing configuration',
                    choices=[
                        app_util.Choice(name='youtube', value=0),
                        app_util.Choice(name='receiver', value=1),
                        app_util.Choice(name='reception', value=2),
                        app_util.Choice(name='ping_role', value=3),
                        app_util.Choice(name='welcome_card', value=4),
                        app_util.Choice(name='custom_message', value=5)
                    ],
                    required=False),

                app_util.StrOption(
                    name='youtube',
                    description='add any youtube channel by URL / ID',
                    required=False),

                app_util.ChannelOption(
                    name='receiver',
                    description='text channel to receive youtube videos',
                    channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
                    required=False),

                app_util.ChannelOption(
                    name='reception',
                    description='text channel to receive welcome cards',
                    channel_types=[app_util.ChannelType.GUILD_TEXT, app_util.ChannelType.GUILD_NEWS],
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
    async def setup_command(self, ctx: app_util.Context):

        await ctx.defer()

        def check(ctx: app_util.Context):
            perms = ctx.channel.permissions_for(ctx.me)
            return perms.send_messages and perms.embed_links and perms.attach_files and perms.external_emojis

        if not isinstance(ctx.author, discord.Member):
            await ctx.send_followup('🚫 This command can only be used inside a **SERVER**')
            return

        if ctx.author.guild_permissions.administrator:

            if not check(ctx):
                await ctx.send_followup(
                    f'> 😓  Please make sure I have permissions to send '
                    f'`messages` `embeds` `custom emojis` `images` (**here**)')
                return

            if not ctx.options:
                await ctx.send_followup('> 👀  you must select at least one option'),
                return

            if ctx.options.get('youtube'):
                url = ctx.options['youtube'].value
                await sub_view_youtube(ctx, url)
            elif ctx.options.get('receiver'):
                channel = ctx.options['receiver'].value
                await sub_view_receiver(ctx, channel)
            elif ctx.options.get('reception'):
                channel = ctx.options['reception'].value
                await sub_view_reception(ctx, channel)
            elif ctx.options.get('ping_role'):
                role = ctx.options['ping_role'].value
                await sub_view_pingrole(ctx, role)
            elif ctx.options.get('welcome_card'):
                cdn_url = ctx.options['welcome_card'].value.url
                await sub_view_welcomecard(ctx, cdn_url)
            elif ctx.options.get('custom_message'):
                value = ctx.options['custom_message'].value
                await sub_view_msg(ctx, value, self.bot)
            elif ctx.options.get('overview'):
                await sub_view_config(ctx.options['overview'].value, ctx)
            elif ctx.options.get('remove'):
                await sub_view_remove(ctx, ctx.options['remove'].value)
        else:
            await ctx.send_followup('> 👀  You are not an **Admin** or **Equivalent**')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Setup(bot))
