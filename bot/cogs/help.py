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
    @app_util.Cog.before_invoke(check_handler=check)
    async def help_command(self, ctx: app_util.Context):
        view = CustomView(ctx)
        emd = discord.Embed(
            title=f'Commands',
            description=f'\n**` 1 `** **`/setup`**'
                        f'\n\n> {Emo.YT} adding YouTube Channel for notifications'
                        f'\n> {Emo.SLASH}`/setup` `youtube` `TYPE CHANNEL URL`'
                        f'\n\n> {Emo.PING} adding default text channel for notifications'
                        f'\n> {Emo.SLASH}`/setup` `receiver` `CHOOSE TEXT CHANNEL`'
                        f'\n\n> {Emo.DEAL} adding a text channel to receive welcome card'
                        f'\n> {Emo.SLASH}`/setup` `reception` `CHOOSE TEXT CHANNEL`'
                        f'\n\n> {Emo.BELL} adding a role to ping users with notifications'
                        f'\n> {Emo.SLASH}`/setup` `ping_role` `CHOOSE A ROLE`'
                        f'\n\n> {Emo.IMG} adding an image to use as welcome greeting card'
                        f'\n> {Emo.SLASH}`/setup` `welcome_card` `ATTACH IMAGE FILE`'
                        f'\n\n> {Emo.CUSTOM} adding a custom message to send with notifications'
                        f'\n> {Emo.SLASH}`/setup` `custom_message` `CHOOSE MESSAGE OPTION`'
                        f'\n\n**` 2 `** **`/more`**'
                        f'\n\n> {Emo.DEL} removing an old settings'
                        f'\n> {Emo.SLASH}`/more` `remove` `CHOOSE SETTING TO REMOVE`'
                        f'\n\n> {Emo.DATABASE} overviewing an old settings'
                        f'\n> {Emo.SLASH}`/more` `overview` `CHOOSE SETTING TO SEE`'
                        f'\n\n**` 3 `** **`/force` `TYPE CHANNEL URL`**'
                        f'\n\n> Force checks channel for new upload or livestream'
                        f'\n\n{Emo.BUG} Having issues? '
                        f'Ask [Development & Support](https://discord.gg/VE5qRFfmG2)',
            color=0x2f3136,
        )
        await ctx.send_response(embed=emd, view=view)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Help(bot))
