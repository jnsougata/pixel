import discord
import traceback
from typing import Any
from extslash import *
from bot.extras.emojis import Emo
from extslash.commands import SlashCog, ApplicationContext, Bot


class CustomView(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
        self.ctx = ctx

        invite = discord.ui.Button(label='Invite', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/invite')
        upvote = discord.ui.Button(label='Upvote', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/vote')

        super().__init__()
        self.value = None
        self.add_item(invite)
        self.add_item(upvote)

    @discord.ui.button(label='Info', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    async def on_timeout(self) -> None:
        pass


class Help(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def check(ctx: ApplicationContext):
        perms = ctx.channel.permissions_for(ctx.me)
        return perms.send_messages and perms.embed_links and perms.attach_files and perms.external_emojis

    def register(self):
        return SlashCommand(name='help', description='information about the features',)

    async def command(self, ctx: ApplicationContext):

        await ctx.defer()

        if not ctx.guild:
            return await ctx.send_followup('🚫 This command can only be used inside a **SERVER**')

        if not self.check(ctx):
            await ctx.send_followup(
                f'{Emo.WARN} Please make sure I have permissions to send '
                f'`messages` `embeds` `custom emojis` `images` (**here**)')
            return

        emd = discord.Embed(
            description=f'\n\n{Emo.SETUP} Start setup using **`/setup`**'
                        f'\n\n{Emo.FAQ} To know more about **setup** tap **`Info`**'
                        f'\n\n{Emo.SUP} Having issues? Join **[Dev & Support](https://discord.gg/VE5qRFfmG2)**',
            color=0x005aef)

        view = CustomView(ctx)
        await ctx.send_followup(embed=emd, view=view)

        await view.wait()
        if view.value:
            emd = discord.Embed(
                title=f'{Emo.INFO} /setup: access all features',
                description=f'\u200b\n{Emo.DEL} **Remove**'
                            f'\nRemoves configuration of a selected option'
                            f'\n\n{Emo.SETUP} **Overview**'
                            f'\nGives an overview of any selected option'
                            f'\n\n{Emo.PING} **Receiver**'
                            f'\nUsed to add or remove a text channel'
                            f'\nto receive youtube alerts for your server'
                            f'\n\n{Emo.YT} **YouTube**'
                            f'\nUsed to add or remove youtube'
                            f'\nchannel to your server for live alerts'
                            f'\n\n{Emo.DEAL} **Reception**'
                            f'\nUsed to add or remove a text'
                            f'\nchannel for receiving welcome cards'
                            f'\n\n{Emo.BELL} **Ping Role**'
                            f'\nUsed to add or remove a custom role'
                            f'\nto be mentioned with the YT Notifications'
                            f'\n\n{Emo.IMG} **Welcome Card**'
                            f'\nUsed to add or remove a welcome card'
                            f'\nfor your server to welcome new members'
                            f'\n\n{Emo.CUSTOM} **Custom Message**'
                            f'\nUsed to add or remove a custom message'
                            f'\nto be sent with YT Alert & Welcome Card',

                color=0x005aef,
            )
            await ctx.edit_response(embed=emd, view=None)

    async def on_error(self, ctx: ApplicationContext, error: Exception):
        phrase = 'Something went wrong, please try again... 😔'
        await ctx.send_response(phrase, ephemeral=True)
        logger = self.bot.get_channel(938059433794240523)
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await logger.send(f'```py\n{tb}\n```')


def setup(bot: Bot):
    bot.add_slash_cog(Help(bot))
