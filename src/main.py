import os
import discord
from discord.ext import commands
from src.extras.func import exe_prefix
from slash import *
from typing import Any
from src.extras.emojis import Emo
from src.views.setupView import BaseView, CommandMenu

intent = discord.Intents().default()
intent.members = True


class PixeL(Client):
    def __init__(self):
        super().__init__(
            intents=intent,
            help_command=None,
            command_prefix=exe_prefix,
        )

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


pixel = PixeL()


cogs = [
    "help",
    "error",
    "welcomer",
    "settings",
    "listener",
    "statusloop",
]

for cog in cogs:
    pixel.load_extension("cogs." + cog)


@pixel.slash_command(SlashCommand(
    name='setup',
    description='Setup PixeL for your Server')
)
async def setup(ctx: ApplicationContext):
    if ctx.author.guild_permissions.administrator:
        emd = discord.Embed(title=f'{Emo.SETUP} use menu below to setup', colour=0x005aef)
        emd.set_footer(text=f'⮞⮞ menu disappears in thirty seconds')
        view = BaseView()
        view.add_item(CommandMenu(ctx, pixel))
        await ctx.respond(embed=emd)
        view.message = await ctx.send(content='\u200b', view=view)
    else:
        await interaction.respond(
            embed=discord.Embed(title=f'{Emo.WARN} You are not an **ADMIN** {Emo.WARN}'), ephemeral=True)


pixel.run(os.getenv('DISCORD_TOKEN'))
