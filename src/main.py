import os
import discord
from discord.ext import commands
from src.extras.func import exe_prefix
from slash import SlashInteraction, SlashBot, Slash
from typing import Any
from src.icog.cmd import setup_command, setup_func

intent = discord.Intents().default()
intent.members = True


class PixeL(SlashBot):
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
    "listener",
    "statusloop",
]

for cog in cogs:
    pixel.load_extension("cogs." + cog)

pixel.add_slash(setup_command, setup_func, 877399405056102431)
pixel.run(os.getenv('DISCORD_TOKEN'))
