import discord
import neocord
from typing import Any
from bot.extras.emojis import Emo


class Help(neocord.cog):

    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(name='help', description='information about the features', options=[
        neocord.IntOption(
            name='command',
            description='shows information about a specific command',
            required=True,
            choices=[
                neocord.Choice('/setup youtube', 1),
                neocord.Choice('/setup welcomer', 2),
                neocord.Choice('/setup ping_role', 3),
                neocord.Choice('/setup custom_message', 4),
                neocord.Choice('/more remove', 5),
                neocord.Choice('/more overview', 6),
                neocord.Choice('/force', 7)
            ])
    ])
    async def help_command(self, ctx: neocord.Context, command: int):
        inv = 'https://top.gg/bot/848304171814879273/invite'
        sup = 'https://discord.gg/VE5qRFfmG2'
        uv = 'https://top.gg/bot/848304171814879273/vote'

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Support', style=discord.ButtonStyle.link, url=sup))
        view.add_item(discord.ui.Button(label='Invite', style=discord.ButtonStyle.link, url=inv))
        view.add_item(discord.ui.Button(label='Upvote', style=discord.ButtonStyle.link, url=uv))

        if command == 1:
            content = (
                f'</setup youtube:936634659763286076>'
                f'\n\nSet up the YouTube channel for the server'
                f'\n\n`channel` url or id of the youtube channel'
                f'\n`receiver` text channel to receive notifications'
            )
        elif command == 2:
            content = (
                f'</setup welcomer:936634659763286076>'
                f'\n\nSet up the welcome message for the server'
                f'\n\n`channel` text channel to greet with welcome cards'
                f'\n`image` image file to send when new member joins'
            )
        elif command == 3:
            content = (
                f'</setup ping_role:936634659763286076>'
                f'\n\nSet up the ping role for the server'
                f'\n\n`role` role to ping with youtube notification'
            )
        elif command == 4:
            content = (
                f'</setup custom_message:936634659763286076>'
                f'\n\nSet up the custom message for the server'
                f'\n\n`option` choose option to setup or edit'
            )
        elif command == 5:
            content = (
                f'</more remove:936634659763286076>'
                f'\n\nRemove a specific option'
                f'\n\n`option` choose option to remove'
            )
        elif command == 6:
            content = (
                f'</more overview:936634659763286076>'
                f'\nShow any current settings'
                f'\n\n`option` choose option to view'
            )
        elif command == 7:
            content = (
                f'</force:936634659763286076>'
                f'\nForce a scans youtube channels for new videos'
            )
        else:
            content = f'\nUnknown command {command}'
        embed = discord.Embed(description=content, color=discord.Color.blue())
        await ctx.send_response(embed=embed, view=view)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Help(bot))
