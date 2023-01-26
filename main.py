import os
import discord
from deta import Deta
from discord.ext import commands

intent = discord.Intents().default()
intent.members = True


class PixeL(commands.Bot):

    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='/', chunk_guilds_at_startup=False)
        self.init_ext = ['cogs.listener']  # rest commands have been mover to serverless functions
        self.db = None
        self.drive = None
        self.cached = None
        self.session = None

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        self.session = self.http._HTTPClient__session
        deta = Deta(session=self.session, loop=self.loop)
        self.db = deta.base(os.getenv('BASE_NAME'))
        self.drive = deta.drive(os.getenv('DRIVE_NAME'))
        await self.build_cache()
        for ext in self.init_ext:
            await self.load_extension(ext)

    async def build_cache(self):
        fields = await self.db.get()
        self.cached = {int(field.pop('key')): field for field in fields}


if __name__ == '__main__':
    PixeL().run(os.getenv('DISCORD_TOKEN'))
