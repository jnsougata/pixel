import discord
import traceback
import extslash
from bot.extras.emojis import Emo
from bot.views.msg_view import sub_view_msg
from bot.views.view_config import sub_view_config
from bot.views.youtube_view import sub_view_youtube
from bot.views.receiver_view import sub_view_receiver
from bot.views.reception_view import sub_view_reception
from bot.views.pingrole_view import sub_view_pingrole
from bot.views.welcome_view import sub_view_welcomecard
from bot.views.remove_config import sub_view_remove


class Setup(extslash.Cog):


    @extslash.Cog.command(
        command=extslash.SlashCommand(
            name='setup',
            description='configure PixeL for your Server',
            options=[
                extslash.IntOption(
                    name='remove',
                    description='remove any old configuration',
                    choices=[
                        extslash.Choice(name='youtube', value=0),
                        extslash.Choice(name='receiver', value=1),
                        extslash.Choice(name='reception', value=2),
                        extslash.Choice(name='ping_role', value=3),
                        extslash.Choice(name='welcome_card', value=4),
                        extslash.Choice(name='custom_message', value=5)
                    ],
                    required=False),
                extslash.IntOption(
                    name='overview',
                    description='overview of existing configuration',
                    choices=[
                        extslash.Choice(name='youtube', value=0),
                        extslash.Choice(name='receiver', value=1),
                        extslash.Choice(name='reception', value=2),
                        extslash.Choice(name='ping_role', value=3),
                        extslash.Choice(name='welcome_card', value=4),
                        extslash.Choice(name='custom_message', value=5)
                    ],
                    required=False),

                extslash.StrOption(
                    name='youtube',
                    description='add any youtube channel by URL / ID',
                    required=False),

                extslash.ChannelOption(
                    name='receiver',
                    description='text channel to receive youtube videos',
                    channel_types=[extslash.ChannelType.GUILD_TEXT, extslash.ChannelType.GUILD_NEWS],
                    required=False),

                extslash.ChannelOption(
                    name='reception',
                    description='text channel to receive welcome cards',
                    channel_types=[extslash.ChannelType.GUILD_TEXT, extslash.ChannelType.GUILD_NEWS],
                    required=False),

                extslash.RoleOption(
                    name='ping_role',
                    description='role to ping with youtube notification',
                    required=False),

                extslash.AttachmentOption(
                    name='welcome_card',
                    description='image file to send when new member joins',
                    required=False),

                extslash.IntOption(
                    name='custom_message',
                    description='custom welcome and notification message',
                    choices=[
                        extslash.Choice(name='upload_message', value=1),
                        extslash.Choice(name='welcome_message', value=0),
                        extslash.Choice(name='livestream_message', value=2),
                    ],
                    required=False),
            ],
        )
    )
    async def setup_command(self, ctx: extslash.ApplicationContext):

        await ctx.defer()

        def check(ctx: extslash.ApplicationContext):
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

            if ctx.options[0].name == 'youtube':
                url = ctx.options[0].value
                await sub_view_youtube(ctx, url)
            elif ctx.options[0].name == 'receiver':
                channel = ctx.options[0].value
                await sub_view_receiver(ctx, channel)
            elif ctx.options[0].name == 'reception':
                channel = ctx.options[0].value
                await sub_view_reception(ctx, channel)
            elif ctx.options[0].name == 'ping_role':
                role = ctx.options[0].value
                await sub_view_pingrole(ctx, role)
            elif ctx.options[0].name == 'welcome_card':
                cdn_url = ctx.options[0].value.url
                await sub_view_welcomecard(ctx, cdn_url)
            elif ctx.options[0].name == 'custom_message':
                value = ctx.options[0].value
                await sub_view_msg(ctx, value)
            elif ctx.options[0].name == 'overview':
                await sub_view_config(ctx.options[0].value, ctx)
            elif ctx.options[0].name == 'remove':
                await sub_view_remove(ctx, ctx.options[0].value)
        else:
            await ctx.send_followup('> 👀  You are not an **Admin** or **Equivalent**')


def setup(bot: extslash.Bot):
    bot.add_slash_cog(Setup())
