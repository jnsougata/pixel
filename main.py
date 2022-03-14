import os
import discord
import app_util

intent = discord.Intents().default()
intent.members = True


class PixeL(app_util.Bot):

    __dirs__ = os.listdir('bot/cogs')

    def __init__(self):
        super().__init__(intents=intent, help_command=None, command_prefix='$_*', chunk_guilds_at_startup=False)
        self.init_ext = ['bot.cogs.' + file[:-3] for file in self.__dirs__ if file.endswith('.py')]

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        for ext in self.init_ext:
            await self.load_extension(ext)


pixel = PixeL()
pixel.run(os.getenv('DISCORD_TOKEN'))
