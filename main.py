import os
import discord
from extslash import commands

intent = discord.Intents().default()
intent.members = True


class PixeL(commands.Bot):
    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='🞽')

    async def on_ready(self):
        print('------')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


def get_extensions():
    files = os.listdir('bot/cogs')
    return ['bot.cogs.' + file[:-3] for file in files if file.endswith('.py')]


pixel = PixeL()

for extension in get_extensions():
    pixel.load_extension(extension)

pixel.run(os.getenv('DISCORD_TOKEN'))
