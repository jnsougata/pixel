import os
import discord
import neocord
from deta import Deta

intent = discord.Intents().default()
intent.members = True


class PixeL(neocord.Bot):

    __dirs__ = os.listdir('cogs')

    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='/', chunk_guilds_at_startup=False)
        self.init_ext = ['cogs.' + file[:-3] for file in self.__dirs__ if file.endswith('.py')]
        self.db = None
        self.drive = None
        self.cached = None

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        deta = Deta(os.getenv('DETA_TOKEN'))
        await deta.connect(session=self.http._HTTPClient__session, loop=self.loop)
        self.db = deta.base('01PIXEL')
        self.drive = deta.drive('PixeL_@11223344')
        await self.build_cache()
        for ext in self.init_ext:
            await self.load_extension(ext)

    async def build_cache(self):
        fields = await self.db.fetch_all()
        self.cached = {int(field.pop('key')): field for field in fields}


if __name__ == '__main__':
    PixeL().run(os.getenv('DISCORD_TOKEN'))
