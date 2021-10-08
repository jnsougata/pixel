import os
import discord
from discord.ext import commands
from src.extras.func import custom_prefix

intent = discord.Intents().default()
intent.members = True


class BOT(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = custom_prefix,
            intents = intent,
            help_command = None
        )

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = BOT()


cogs = [
    "Set",
    "Help",
    "Error",
    "Remove",
]

for cog in cogs:
    bot.load_extension("cogs." + cog)

bot.run(os.getenv('DISCORD_TOKEN'))