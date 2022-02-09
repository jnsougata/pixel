import discord
import traceback
from typing import Any
from extslash import *
from src.extras.emojis import Emo
from src.extras.func import db_fetch_prefix
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
        return perms.embed_links and perms.attach_files and perms.external_emojis

    def register(self):
        return SlashCommand(name='help', description='PixeL\'s help menu')

    async def command(self, ctx: ApplicationContext):

        if not self.check(ctx):
            await ctx.send_response(
                'Please make sure here I have permissions to send `embeds` `buttons` `emojis` `attachments`',
                ephemeral=True)
            return

        prefix = await db_fetch_prefix(ctx.guild.id)
        emd = discord.Embed(
            description=f'\n\n{Emo.SETUP} Start setup using **`{prefix}setup`** or **`/setup`**'
                        f'\n\n{Emo.FAQ} To know more about **setup** tap **`Info`**'
                        f'\n\n{Emo.SUP} Having issues? Join **[Dev & Support](https://discord.gg/VE5qRFfmG2)**',
            color=0x005aef)

        view = CustomView(ctx)
        await ctx.send_response(embed=emd, view=view)

        await view.wait()
        if view.value:
            emd = discord.Embed(
                description=f'{Emo.INFO} Access all of these'
                            f'\nfollowing options by only using **/setup**'
                            f'\n\n{Emo.TAG}**Prefix**'
                            f'\nUsed to add or remove custom prefix '
                            f'\nto your server. you can change it anytime'
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
                            f'\n\n{Emo.CUSTOM} **Customize Message**'
                            f'\nUsed to add or remove a custom message'
                            f'\nto be sent with Youtube Alert or Welcome Card',

                color=0x005aef,
            )
            await ctx.edit_response(embed=emd, view=None)

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
    bot.add_slash_cog(Help(bot))
