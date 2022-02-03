import discord
from typing import Any
from src.extras.emojis import Emo
from src.views.aux_view import BaseView, CommandMenu
from extslash import *
from extslash.commands import SlashCog, ApplicationContext, Bot


class Setup(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return SlashCommand(name='setup', description='Setup PixeL for your Server')

    async def command(self, ctx: ApplicationContext):
        if ctx.author.guild_permissions.administrator:
            if ctx.channel.permissions_for(ctx.guild.me).use_slash_commands:
                emd = discord.Embed(title=f'{Emo.SETUP} use menu below to setup', colour=0x005aef)
                emd.set_footer(text=f'⏱️ this menu will disappear after 3 minutes')
                view = BaseView()
                view.add_item(CommandMenu(ctx, self.bot))
                await ctx.defer()
                view.message = await ctx.followup.send(embed=emd, view=view)
            else:
                await ctx.respond('I need permission to use slash commands here to use this command',
                                  ephemeral=True)
        else:
            await ctx.respond(
                embed=discord.Embed(title=f'{Emo.WARN} You are not an **ADMIN** {Emo.WARN}'), ephemeral=True)


def setup(bot: Bot):
    bot.add_slash_cog(Setup(bot))
