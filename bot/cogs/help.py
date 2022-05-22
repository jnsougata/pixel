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

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.attach_files and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
        return False
    else:
        return True


class Help(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(name='help', description='information about the features')
    )
    @app_util.Cog.check(check)
    async def help_command(self, ctx: app_util.Context):
        view = CustomView(ctx)
        emd = discord.Embed(
            title=f'Commands',
            description=f'\n**` 1 `** **` /setup `**\n'
                        f'\n {Emo.YT} Adding YouTube Channel for notifications'
                        f'\n```diff\n-❯ /setup youtube: TYPE CHANNEL URL\n```'
                        f'\n {Emo.PING} Adding default text channel for notifications'
                        f'\n```diff\n-❯ /setup receiver: CHOOSE TEXT CHANNEL\n```'
                        f'\n {Emo.DEAL} Adding a text channel to receive welcome card'
                        f'\n```diff\n-❯ /setup reception: CHOOSE TEXT CHANNEL\n```'
                        f'\n {Emo.BELL} Adding a role to ping users with notifications'
                        f'\n```diff\n-❯ /setup ping_role: CHOOSE A ROLE\n```'
                        f'\n {Emo.IMG} Adding an image to use as welcome greeting card'
                        f'\n ```diff\n-❯ /setup welcome_card: ATTACH IMAGE FILE\n```'
                        f'\n {Emo.CUSTOM} Adding a custom message to send with notifications'
                        f'\n```diff\n-❯ /setup custom_message: CHOOSE MESSAGE TYPE\n```'
                        f'\n\n**` 2 `** **` /more `**\n'
                        f'\n {Emo.DEL} Removing an old settings'
                        f'\n```diff\n-❯ /more remove: CHOOSE SETTING TO REMOVE\n```'
                        f'\n {Emo.DATABASE} overviewing an old settings'
                        f'\n```diff\n-❯ /more overview: CHOOSE SETTING TO SEE\n```'
                        f'\n\n**` 3 `** **` /force ` `TYPE CHANNEL URL`**'
                        f'\n```diff\n-❯ Force checks all channels for new videos\n```'
                        f'\n\n{Emo.BUG} Having issues? '
                        f'Ask [Development & Support](https://discord.gg/VE5qRFfmG2)',
            color=0xc62c28,
        )
        await ctx.send_response(embed=emd, view=view)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Help(bot))
