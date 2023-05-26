import os
import discord
from deta import Deta
from discord.ext import commands

intent = discord.Intents().default()
intent.members = True  # noqa


class PixeL(commands.Bot):

    extensions = ['cogs.alert', 'cogs.counter', 'cogs.listener']

    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='/', chunk_guilds_at_startup=False)
        self.db = None
        self.drive = None
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        deta = Deta(loop=self.loop)
        self.db = deta.base(os.getenv('BASE_NAME'))
        self.drive = deta.drive(os.getenv('DRIVE_NAME'))
        for extension in self.extensions:
            await self.load_extension(extension)


if __name__ == '__main__':
    PixeL().run(os.getenv('DISCORD_TOKEN'))
