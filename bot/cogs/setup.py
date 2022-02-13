import discord
import traceback
import extslash as ext
from bot.extras.emojis import Emo
from bot.views.msg_view import sub_view_msg
from bot.views.view_config import sub_view_config
from bot.views.youtube_view import sub_view_youtube
from bot.views.receiver_view import sub_view_receiver
from bot.views.reception_view import sub_view_reception
from bot.views.pingrole_view import sub_view_pingrole
from bot.views.welcome_view import sub_view_welcomecard
from bot.views.remove_config import sub_view_remove
from extslash.commands import SlashCog, ApplicationContext, Bot


class Setup(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def check(ctx: ApplicationContext):
        perms = ctx.channel.permissions_for(ctx.me)
        return perms.send_messages and perms.embed_links and perms.attach_files and perms.external_emojis

    def register(self):
        return ext.SlashCommand(
            name='setup',
            description='configure PixeL for your Server',
            options=[
                ext.IntOption(
                    name='remove',
                    description='remove any old configuration',
                    choices=[
                        ext.Choice(name='youtube', value=0),
                        ext.Choice(name='receiver', value=1),
                        ext.Choice(name='reception', value=2),
                        ext.Choice(name='ping_role', value=3),
                        ext.Choice(name='welcome_card', value=4),
                        ext.Choice(name='custom_message', value=5)
                    ],
                    required=False),
                ext.IntOption(
                    name='overview',
                    description='overview of existing configuration',
                    choices=[
                        ext.Choice(name='youtube', value=0),
                        ext.Choice(name='receiver', value=1),
                        ext.Choice(name='reception', value=2),
                        ext.Choice(name='ping_role', value=3),
                        ext.Choice(name='welcome_card', value=4),
                        ext.Choice(name='custom_message', value=5)
                    ],
                    required=False),

                ext.StrOption(
                    name='youtube',
                    description='add any youtube channel by URL / ID',
                    required=False),

                ext.ChannelOption(
                    name='receiver',
                    description='text channel to receive youtube videos',
                    channel_types=[ext.ChannelType.GUILD_TEXT, ext.ChannelType.GUILD_NEWS],
                    required=False),

                ext.ChannelOption(
                    name='reception',
                    description='text channel to receive welcome cards',
                    channel_types=[ext.ChannelType.GUILD_TEXT, ext.ChannelType.GUILD_NEWS],
                    required=False),

                ext.RoleOption(
                    name='ping_role',
                    description='role to ping with youtube notification',
                    required=False),

                ext.AttachmentOption(
                    name='welcome_card',
                    description='image file to send when new member joins',
                    required=False),

                ext.IntOption(
                    name='custom_message',
                    description='custom welcome and notification message',
                    choices=[
                        ext.Choice(name='upload_message', value=1),
                        ext.Choice(name='welcome_message', value=0),
                        ext.Choice(name='livestream_message', value=2),
                    ],
                    required=False),
            ],
        )

    async def command(self, ctx: ApplicationContext):

        await ctx.defer()

        if not isinstance(ctx.author, discord.Member):
            await ctx.send_followup('🚫 This command can only be used inside a **SERVER**')
            return

        if ctx.author.guild_permissions.administrator:

            if not self.check(ctx):
                await ctx.send_followup(
                    f'> 😓  Please make sure I have permissions to send '
                    f'`messages` `embeds` `custom emojis` `images` (**here**)')
                return

            if not ctx.options:
                await ctx.send_followup('> 👀  you must select at least one option'),
                return

            if ctx.options[0].name == 'youtube':
                url = ctx.options[0].value
                await sub_view_youtube(ctx, self.bot, url)
            elif ctx.options[0].name == 'receiver':
                channel = ctx.options[0].value
                await sub_view_receiver(ctx, self.bot, channel)
            elif ctx.options[0].name == 'reception':
                channel = ctx.options[0].value
                await sub_view_reception(ctx, self.bot, channel)
            elif ctx.options[0].name == 'ping_role':
                role = ctx.options[0].value
                await sub_view_pingrole(ctx, self.bot, role)
            elif ctx.options[0].name == 'welcome_card':
                cdn_url = ctx.options[0].value.url
                await sub_view_welcomecard(ctx, self.bot, cdn_url)
            elif ctx.options[0].name == 'custom_message':
                value = ctx.options[0].value
                await sub_view_msg(ctx, self.bot, value)
            elif ctx.options[0].name == 'overview':
                await sub_view_config(ctx.options[0].value, ctx)
            elif ctx.options[0].name == 'remove':
                await sub_view_remove(ctx, ctx.options[0].value)
        else:
            await ctx.send_followup('> 👀  You are not an **Admin** or **Equivalent**')

    async def on_error(self, ctx: ApplicationContext, error: Exception):
        await ctx.send_followup('Something went wrong, please try again... 😔')
        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await logger.send(f'```py\n{tb}\n```')


def setup(bot: Bot):
    bot.add_slash_cog(Setup(bot))
