import os
import neocord
import asyncio
import discord
import traceback
from deta import Field
from extras.emoji import Emo

class Force(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    @neocord.cog.command(name='force', description='forces to check for new videos', dm_access=False)
    async def force_check(self, ctx: neocord.Context):
        channels = self.bot.cached[ctx.guild.id].get('CHANNELS')
        await ctx.defer()
        embed = discord.Embed(description=f'> {Emo.WARN} This command has been deprecated and will be removed in future.')
        await ctx.send_followup(embed=embed)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Force(bot))
