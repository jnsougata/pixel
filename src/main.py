import os
import discord
from src.extras.func import exe_prefix
from src.extras.emojis import Emo
from extslash.commands import Client

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

pixel.load_slash_extension('icog.setup')
pixel.run(os.getenv('DISCORD_TOKEN'))
