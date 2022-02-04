import discord
from typing import Any
from src.extras.emojis import Emo
from extslash import *
from src.extras.func import db_fetch_prefix
from extslash.commands import SlashCog, ApplicationContext, Bot


class CustomView(discord.ui.View):
    def __init__(
            self,
            ctx: ApplicationContext,
            message: discord.Message = None
    ):
        self.ctx = ctx
        self.message = message

        invite = discord.ui.Button(label='Invite', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/invite')
        upvote = discord.ui.Button(label='Upvote', style=discord.ButtonStyle.link,
                                   url='https://top.gg/bot/848304171814879273/vote')

        super().__init__()
        self.value = None
        self.timeout = 120
        self.add_item(invite)
        self.add_item(upvote)

    @discord.ui.button(label='Info', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except Exception:
            pass


class Setup(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return SlashCommand(name='help', description='PixeL\'s help menu')

    async def command(self, ctx: ApplicationContext):
        await ctx.defer()

        if ctx.channel.permissions_for(ctx.guild.me).use_slash_commands:

            def has_perms(ctx_: ApplicationContext):
                perms = ctx_.channel.permissions_for(ctx_.guild.me)
                return perms.embed_links and perms.attach_files and perms.external_emojis

            if not has_perms(ctx):
                await ctx.followup.send(
                    'Please make sure here I have permissions to send `embeds` `buttons` `emojis` `attachments`')
                return

            prefix = await db_fetch_prefix(ctx.guild.id)
            emd = discord.Embed(
                description=f'\n\n{Emo.SETUP} Start setup using **`{prefix}setup`** or **`/setup`**'
                            f'\n\n{Emo.FAQ} To know more about **setup** tap **`Info`**'
                            f'\n\n{Emo.SUP} Having issues? Join **[Dev & Support](https://discord.gg/VE5qRFfmG2)**',
                color=0x005aef)

            view = CustomView(ctx)
            message = await ctx.followup.send(embed=emd, view=view)

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
                await message.edit(embed=emd, view=None)
        else:
            await ctx.followup.send('Please make sure I have permission here to use `Slash Commands`')


def setup(bot: Bot):
    bot.add_slash_cog(Setup(bot))
