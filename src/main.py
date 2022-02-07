import os
import discord
from src.extras.func import exe_prefix
from src.extras.emojis import Emo
from extslash.commands import Bot

intent = discord.Intents().default()
intent.members = True


class PixeL(Bot):
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

cogs = ["eh", "help", "settings", "listener", "statusloop"]
icogs = ['help', 'setup']

for cog in cogs:
    pixel.load_extension("cogs." + cog)

for icog in icogs:
    pixel.load_extension("icogs." + icog)

pixel.run(os.getenv('DISCORD_TOKEN'))
