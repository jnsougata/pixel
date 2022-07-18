import discord
import neocord
import traceback
from typing import Any
from bot.extras.emojis import Emo


class Help(neocord.cog):

    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(name='help', description='information about the features', category=neocord.CommandType.SLASH)
    async def help_command(self, ctx: neocord.Context):
        emd = discord.Embed(
            title=f'Commands',
            description=f'\n**` 1 `** **` /setup `**\n'
                        f'\n```diff\n■ setting up youtube'
                        f'\n-❯ /setup youtube <url/id> <text channel>\n```'
                        f'```diff\n■ setting up welcomer'
                        f'\n-❯ /setup welcomer <text channel> <image>\n```'
                        f'```diff\n■ setting up a ping role'
                        f'\n-❯ /setup ping_role <role>\n```'
                        f'```diff\n■ setting up custom message'
                        f'\n-❯ /setup custom_message <option>\n```'
                        f'\n\n**` 2 `** **` /more `**\n'
                        f'\n```diff\n■ removing an old settings'
                        f'\n-❯ /more remove: CHOOSE SETTING TO REMOVE\n```'
                        f'```diff\n■ overviewing an old settings'
                        f'\n-❯ /more overview: CHOOSE SETTING TO SEE\n```'
                        f'\n\n**` 3 `** **` /force `**'
                        f'\n```diff\n■ force checking for new videos'
                        f'\n-❯ /force\n```'
                        f'\n{Emo.BUG} Ask [development & support](https://discord.gg/VE5qRFfmG2) '
                        f' ■ [Invite](https://top.gg/bot/848304171814879273/invite) '
                        f' ■ [Upvote](https://top.gg/bot/848304171814879273/vote)',
            color=0xc62c28,
        )
        await ctx.send_response(embed=emd)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Help(bot))
