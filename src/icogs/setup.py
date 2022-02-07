import discord
from typing import Any
from src.extras.emojis import Emo
from src.iviews.aux_view import BaseView, CommandMenu
from extslash import *
from extslash.commands import SlashCog, ApplicationContext, Bot


class Setup(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return SlashCommand(name='setup', description='Setup PixeL for your Server')

    async def command(self, ctx: ApplicationContext):

        def has_perms(ctx_: ApplicationContext):
            perms = ctx_.channel.permissions_for(ctx_.guild.me)
            return perms.embed_links and perms.attach_files and perms.external_emojis

        if ctx.author.guild_permissions.administrator:

            if ctx.channel.permissions_for(ctx.guild.me).use_slash_commands:

                if not has_perms(ctx):
                    await ctx.followup.send(
                        'Please make sure here I have permissions to send `embeds` `buttons` `emojis` `attachments`')
                    return

                emd = discord.Embed(title=f'{Emo.SETUP} use menu below to setup', colour=0x005aef)
                emd.set_footer(text=f'⏱️ this menu will disappear after 3 minutes')
                view = BaseView()
                view.add_item(CommandMenu(ctx, self.bot))
                await ctx.send_response(embed=emd, view=view)
            else:
                await ctx.send_response('Please make sure I have permission here to use `Slash Commands`',
                                        ephemeral=True)
        else:
            await ctx.send_response(f'You are not an **Admin** or **Equivalent**', ephemeral=True)


def setup(bot: Bot):
    bot.add_slash_cog(Setup(bot))
