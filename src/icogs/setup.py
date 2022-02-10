import discord
import traceback
import extslash as ext
from src.extras.emojis import Emo
from src.iviews.aux_view import BaseView, CommandMenu
from extslash.commands import SlashCog, ApplicationContext, Bot


class Setup(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def check(ctx: ApplicationContext):
        perms = ctx.channel.permissions_for(ctx.me)
        return perms.embed_links and perms.attach_files and perms.external_emojis

    def register(self):
        return ext.SlashCommand(name='setup', description='Setup PixeL for your Server')

    async def command(self, ctx: ApplicationContext):

        if not isinstance(ctx.author, discord.Member):
            await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
            return

        if ctx.author.guild_permissions.administrator:

            if not self.check(ctx):
                await ctx.send_response(
                    'Please make sure here I have permissions to send `embeds` `buttons` `emojis` `attachments`',
                    ephemeral=True)
                return

            emd = discord.Embed(title=f'{Emo.SETUP} use menu below to setup', colour=0x005aef)
            emd.set_footer(text=f'⏱️ this menu will disappear after 3 minutes')
            view = BaseView()
            view.add_item(CommandMenu(ctx, self.bot))
            await ctx.send_response(embed=emd, view=view)
        else:
            await ctx.send_response(f'You are not an **Admin** or **Equivalent**', ephemeral=True)

    async def on_error(self, ctx: ApplicationContext, error: Exception):
        phrase = 'Something went wrong, please try again... 😔'
        if ctx.responded:
            await ctx.send_followup(phrase, ephemeral=True)
        else:
            await ctx.send_response(phrase, ephemeral=True)

        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await logger.send(f'```py\n{tb}\n```')


def setup(bot: Bot):
    bot.add_slash_cog(Setup(bot))
