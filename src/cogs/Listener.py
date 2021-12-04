import discord.errors
from discord.ext import commands
from src.extras.emojis import Emo


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup geeks. I\'m **PixeL**'
                        f'\n\nTo get started, send `.help` | `@{guild.me.display_name} help` '
                        f'\n\nUse any one commands for everything:'
                        f'\n`.settings` | `.setup`'
                        f'\n\n**Important Links**'
                        f'\n[Invite]({invite}) - Add the bot to another server'
                        f'\n[Support Server]({support}) - Get some bot support for issues!',
            color=0xf2163b,
        )
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(embed=emd)
                    break
                except discord.errors.Forbidden:
                    continue

        registry = self.bot.get_channel(899864601057976330)
        await registry.send(
            embed=discord.Embed(
                title=f'{Emo.MIC} Guild Added:',
                description=f'`Name`   **{guild.name}**'
                            f'\n\n`Id`   **{guild.id}**',
                colour=discord.Colour.blurple()
            )
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        registry = self.bot.get_channel(899864601057976330)
        await registry.send(
            embed=discord.Embed(
                title=f'{Emo.MIC} Guild Removed:',
                description=f'`Name`   **{guild.name}**'
                            f'\n\n`Id`   **{guild.id}**',
                colour=discord.Colour.red()
            )
        )


def setup(bot):
    bot.add_cog(Listeners(bot))
