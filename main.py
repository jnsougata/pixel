import os
import discord
import logging
from deta import Deta
from discord.ext import commands

intent = discord.Intents().default()
intent.members = True  # noqa


class PixeL(commands.Bot):

    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='/', chunk_guilds_at_startup=False)
        self.db = None
        self.drive = None
        self.log_channel_id = None

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        deta = Deta(loop=self.loop)
        self.db = deta.base(os.getenv('BASE_NAME'))
        self.drive = deta.drive(os.getenv('DRIVE_NAME'))
        await self.load_extensions_from('cogs')
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))

    async def load_extensions_from(self, path: str) -> None:
        cogs = [
            f'{path}.{module[:-3]}'
            for module in os.listdir(path) if module.endswith('.py')
        ]
        for cog in cogs:
            await self.load_extension(cog)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    PixeL().run(os.getenv('DISCORD_TOKEN'))
