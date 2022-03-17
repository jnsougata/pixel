import discord
import app_util
import traceback
from typing import Any
from bot.extras.emojis import Emo


class CustomView(discord.ui.View):
    def __init__(self, ctx: app_util.Context):
        self.ctx = ctx

        invite = discord.ui.Button(label='Invite', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/invite')
        upvote = discord.ui.Button(label='Upvote', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/vote')

        super().__init__()
        self.value = None
        self.add_item(invite)
        self.add_item(upvote)

    async def on_timeout(self) -> None:
        pass


async def check(ctx: app_util.Context):

    def check():
        p = ctx.channel.permissions_for(ctx.me)
        return p.send_messages and p.embed_links and p.attach_files and p.external_emojis

    if not ctx.guild:
        await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
    elif not check():
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    else:
        return True


class Help(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(name='help', description='information about the features')
    )
    @app_util.Cog.before_invoke(check=check)
    async def help_command(self, ctx: app_util.Context):
        view = CustomView(ctx)
        emd = discord.Embed(
            description=f'\n{Emo.SLASH}**setup**'
                        f'\n\n> {Emo.YT} `YouTube`'
                        f'\n> adds youtube channel for notifications'
                        f'\n\n> {Emo.PING} `Receiver`'
                        f'\n> adds a text channel to receive notifications'
                        f'\n\n> {Emo.DEAL} `Reception`'
                        f'\n> adds a text channel to receive welcome card'
                        f'\n\n> {Emo.BELL} `Ping Role`'
                        f'\n> adds a role to ping users with notifications'
                        f'\n\n> {Emo.IMG} `Welcome Card`'
                        f'\n> adds an image to use as welcome greeting card'
                        f'\n\n> {Emo.CUSTOM} `Custom Message`'
                        f'\n> adds a custom message to send with notifications'
                        f'\n\n{Emo.SLASH}**more**'
                        f'\n\n> {Emo.DEL} `Remove`'
                        f'\n> removes old settings of the selected option'
                        f'\n\n> {Emo.DATABASE} `Overview`'
                        f'\n> shows an overview about the previously set option'
                        f'\n\n{Emo.SLASH}**force**'
                        f'\n> forces the bot to check for new videos or livestreams'
                        f'\n\n{Emo.BUG} Having issues? '
                        f'Ask [Development & Support](https://discord.gg/VE5qRFfmG2)',
            color=0x2f3136,
        )
        await ctx.send_response(embed=emd, view=view)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Help(bot))
