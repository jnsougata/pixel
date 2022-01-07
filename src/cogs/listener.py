import discord
import discord.errors
from discord.ext import commands
from src.extras.emojis import Emo


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        invite = 'https://top.gg/bot/848304171814879273/invite'
        support = 'https://discord.gg/G9fk5HHkZ5'
        emd = discord.Embed(
            description=f'{Emo.MIC} Sup folks! I\'m **PixeL**'
                        f'\n\nTo get started, send `.help` | `@{guild.me.display_name} help` '
                        f'\n\nUse any one commands for everything:'
                        f'\n`.settings` | `.setup`'
                        f'\n\n**Important Links**'
                        f'\n[Invite]({invite}) - Add the bot to another server'
                        f'\n[Support Server]({support}) - Get some bot support here!',
            color=0xf2163b,
        )

        async def get_valid_prompt_channel(_guild: discord.Guild):
            for txt_ch in _guild.text_channels:
                if txt_ch.permissions_for(guild.me).send_messages:
                    return txt_ch

        prompt_channel = await get_valid_prompt_channel(guild)

        try:
            await prompt_channel.send(embed=emd)
        except discord.errors.Forbidden:
            pass
        finally:
            registry = self.bot.get_channel(899864601057976330)
            try:
                invite = await prompt_channel.create_invite(max_age=0, max_uses=0, unique=False)
                url = invite.url
            except Exception:
                url = None

            await registry.send(
                embed=discord.Embed(
                    title=f'{Emo.MIC} {guild.name}',
                    description=f'**`Owner`** {guild.owner}'
                                f'\n\n**`Members`** {guild.member_count}'
                                f'\n\n**`ID`** **`{guild.id}`**'
                                f'\n\n**`Invite URL`** {url}',
                    colour=discord.Colour.blurple()
                )
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        registry = self.bot.get_channel(899864601057976330)
        await registry.send(
            embed=discord.Embed(
                title=f'{Emo.MIC} {guild.name}',
                description=f'Inspect for black-listing trace.'
                            f'\nGuild ID: `{guild.id}`',
                colour=discord.Colour.red()
            )
        )


def setup(bot):
    bot.add_cog(Listeners(bot))
