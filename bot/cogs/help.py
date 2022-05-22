import discord
import app_util
import traceback
from typing import Any
from bot.extras.emojis import Emo


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
                        f'\n```diff\n■ adding youtube channel'
                        f'\n-❯ /setup youtube: TYPE CHANNEL URL\n```'
                        f'\n```diff\n■ adding default noti channel'
                        f'\n-❯ /setup receiver: CHOOSE TEXT CHANNEL\n```'
                        f'\n```diff\n■ adding channel for welcome card'
                        f'\n-❯ /setup reception: CHOOSE TEXT CHANNEL\n```'
                        f'\n```diff\n■ adding a ping role'
                        f'\n-❯ /setup ping_role: CHOOSE A ROLE\n```'
                        f'\n ```diff\n■ adding an image as welcome card'
                        f'\n-❯ /setup welcome_card: ATTACH IMAGE FILE\n```'
                        f'\n```diff\n■ adding custom notification message'
                        f'\n-❯ /setup custom_message: CHOOSE MESSAGE TYPE\n```'
                        f'\n\n**` 2 `** **` /more `**\n'
                        f'\n```diff\n■ removing an old settings'
                        f'\n-❯ /more remove: CHOOSE SETTING TO REMOVE\n```'
                        f'\n```diff\n■ overviewing an old settings'
                        f'\n-❯ /more overview: CHOOSE SETTING TO SEE\n```'
                        f'\n\n**` 3 `** **` /force `**'
                        f'\n```diff\n■ force checking for new videos'
                        f'\n-❯ /force TYPE CHANNEL URL\n```'
                        f'\n{Emo.BUG} Ask [development & support](https://discord.gg/VE5qRFfmG2) '
                        f' ■ [Invite](https://top.gg/bot/848304171814879273/invite) '
                        f' ■ [Upvote](https://top.gg/bot/848304171814879273/vote)',
            color=0xc62c28,
        )
        await ctx.send_response(embed=emd)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Help(bot))
