import os
import discord
from discord.ext import commands
from src.extras.func import exec_prefix

intent = discord.Intents().default()
intent.members = True


class PixeL(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=intent,
            help_command=None,
            command_prefix=exec_prefix,
        )

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


pixel = PixeL()
pixel.load_extension("cogs._sync")
pixel.run('----')
