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
        print('------')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


if __name__ == '__main__':
    pixel = PixeL()
    bucket = []
    bucket.extend([f'cogs.{file[:-3]}' for file in os.listdir('cogs') if file.endswith('.py')])
    bucket.extend([f'icogs.{file[:-3]}' for file in os.listdir('icogs') if file.endswith('.py')])
    for ext in bucket:
        pixel.load_extension(ext)
    pixel.run(os.getenv('DISCORD_TOKEN'))
