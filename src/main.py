import os
import discord
from discord.ext import commands
from src.extras.func import custom_prefix

intent = discord.Intents().default()
intent.members = True


class PixeL(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=custom_prefix,
            intents=intent,
            help_command=None
        )

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


pixel = PixeL()


cogs = [
    "help",
    "owner",
    "error",
    "activity",
    "welcomer",
    "settings",
    "listener",
]

for cog in cogs:
    pixel.load_extension("cogs." + cog)

pixel.run(os.getenv('DISCORD_TOKEN'))
