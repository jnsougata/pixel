import discord
import app_util
import traceback
from typing import Any
from bot.extras.emojis import Emo
from bot.extras.func import drive, db_fetch_object
import os
import aiohttp
from asyncdeta import Deta, Field, Update


class Override(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='override',
            description='override any server configuration with owner privileges', default_access=False,
            options=[
                app_util.StrOption(name='guild_id', description='id of the target guild', required=True),
                app_util.AttachmentOption(name='welcome_card', description='welcome card for the guild', required=False),
                app_util.BoolOption(name='purge', description='removes a guild from the bot', required=False),
            ],
            overwrites=[app_util.Overwrite.for_user(516649677001719819)]
        ),
        guild_id=877399405056102431
    )
    async def override_command(self, ctx: app_util.Context, guild_id: str, welcome_card: discord.Attachment, purge: bool):
        await ctx.defer()

        if welcome_card:
            emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card Updated')
            emd.set_image(url=welcome_card.url)
            emd.set_footer(text=f'Target Guild (ID: {guild_id})')
            await ctx.send_followup(embed=emd)

            def upload():
                drive.upload_from_url(welcome_card.url, f'covers/{guild_id}_card.png')

            self.bot.loop.run_in_executor(None, upload)

        if purge:
            guild = await self.bot.fetch_guild(int(guild_id))
            await guild.leave()
            await ctx.send_followup(embed=discord.Embed(title=f'{Emo.CHECK} Guild Purged ({guild.id})'))

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='sync',
            description='syncs base to base', default_access=False,
            options=[
                app_util.IntOption(
                    name='option',
                    description='option to sync',
                    required=True,
                    choices=[
                        app_util.Choice(name='channels', value=1),
                        app_util.Choice(name='customs', value=2),
                        app_util.Choice(name='receptions', value=3),
                        app_util.Choice(name='receivers', value=4),
                        app_util.Choice(name='ping_roles', value=5),
                    ],
                ),
            ],
            overwrites=[app_util.Overwrite.for_user(516649677001719819)]
        ),
        guild_id=877399405056102431
    )
    async def sync_command(self, ctx: app_util.Context, option: int):
        await ctx.send_response('Check terminal. Sync in progress...')

        if option == 1:
            for guild in self.bot.guilds:
                old_channels = await db_fetch_object(guild_id=guild.id, key='youtube')
                old_receivers = await db_fetch_object(guild_id=guild.id, key='receivers')
                if old_channels and old_receivers:
                    for channel in old_channels.keys():
                        receiver = old_receivers.get(channel)
                        old_channels[channel]['receiver'] = receiver
                    await self.bot.db.add_field(key=str(guild.id), field=Field('CHANNELS', old_channels), force=True)
                    print(old_channels)
            await ctx.send_followup('[CHANNELS] Sync complete...')

        if option == 2:
            for guild in self.bot.guilds:
                old_texts = await db_fetch_object(guild_id=guild.id, key='text') or {}
                await self.bot.db.add_field(key=str(guild.id), field=Field('CUSTOM', old_texts), force=True)
                print(old_texts)
            await ctx.send_followup('[CUSTOM] Sync complete...')

        if option == 3:
            for guild in self.bot.guilds:
                old_reception = await db_fetch_object(guild_id=guild.id, key='welcome')
                data = old_reception[0] if old_reception and old_reception[0].isdigit() else None
                await self.bot.db.add_field(key=str(guild.id), field=Field('RECEPTION', data), force=True)
                print(old_reception)
            await ctx.send_followup('[RECEPTION] Sync complete...')

        if option == 4:
            for guild in self.bot.guilds:
                old_receiver = await db_fetch_object(guild_id=guild.id, key='alertchannel')
                data = old_receiver[0] if old_receiver and old_receiver[0].isdigit() else None
                await self.bot.db.add_field(key=str(guild.id), field=Field('RECEIVER', data), force=True)
                print(old_receiver)
            await ctx.send_followup('[RECEIVER] Sync complete...')

        if option == 5:
            for guild in self.bot.guilds:
                old_ping_role = await db_fetch_object(guild_id=guild.id, key='arole')
                data = old_ping_role[0] if old_ping_role and old_ping_role[0].isdigit() else None
                await self.bot.db.add_field(key=str(guild.id), field=Field('PINGROLE', data), force=True)
                print(old_ping_role)
            await ctx.send_followup('[PINGROLE] Sync complete...')


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Override(bot))
