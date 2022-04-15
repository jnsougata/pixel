import discord
import app_util
import traceback
from typing import Any
from bot.extras.emojis import Emo
from bot.extras.func import drive


class User:
    def __init__(self, id: int):
        self.id = id



class Override(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='override',
            description='override any server configuration with owner privileges', default_access=False,
            options=[
                app_util.StrOption(name='guild_id', description='id of the target guild', required=True),
                app_util.AttachmentOption(name='welcome_card', description='welcome card for the guild', required=False),
                app_util.BoolOption(name='purge', description='removes a guild from the bot', required=False),
            ],
            overwrites=[app_util.Overwrite.for_user(516649677001719819)]
        ),
        guild_id=877399405056102431
    )
    async def override_command(self, ctx: app_util.Context, guild_id: str, welcome_card: discord.Attachment, purge: bool):
        await ctx.defer()

        if welcome_card:
            emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card Updated')
            emd.set_image(url=welcome_card.url)
            emd.set_footer(text=f'Target Guild (ID: {guild_id})')
            await ctx.send_followup(embed=emd)

            def upload():
                drive.upload_from_url(welcome_card.url, f'covers/{guild_id}_card.png')

            self.bot.loop.run_in_executor(None, upload)

        if purge:
            guild = await self.bot.fetch_guild(int(guild_id))
            await guild.leave()
            await ctx.send_followup(embed=discord.Embed(title=f'{Emo.CHECK} Guild Purged ({guild.id})'))


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Override(bot))
