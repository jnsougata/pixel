import os
import neocord
import asyncio
import discord
import traceback
from deta import Field
from extras.emoji import Emo
from extras.utils import (
    create_menu,
    fetch_latest_uploaded,
    fetch_current_livestream,
    fetch_channel_info
)


async def log_exception(channel: discord.TextChannel, guild: discord.Guild, error: Exception):
    stack = traceback.format_exception(type(error), error, error.__traceback__)
    tb = ''.join(stack)
    await channel.send(embed=discord.Embed(
        title=f'Exception occurred during Scanning',
        description=f'**Guild: {guild.name} | ID: {guild.id}**\n```py\n{tb}\n```'))


async def create_ping(guild: discord.guild, cache: dict):
    role_id = cache.get('PINGROLE')
    if not (role_id and role_id.isdigit()):
        return
    role = guild.get_role(int(role_id))
    if role and role == guild.default_role:
        return '@everyone'
    elif role:
        return role.mention


async def create_receiver(guild: discord.Guild, youtube_id: str, cache: dict):
    receiver_id = cache['CHANNELS'][youtube_id]['receiver']
    if not (receiver_id and receiver_id.isdigit()):
        return
    return guild.get_channel(int(receiver_id))


async def custom_message(event: str, guild: discord.Guild, channel_name: str, video_url: str, cache: dict):
    ping = await create_ping(guild, cache)
    scopes = {'[ping]': ping or '', '[name]': channel_name, '[url]': video_url}
    data = cache.get('CUSTOM')
    if not (data and data.get(event)):
        return
    text = data.get(event)
    if '[url]' not in text:
        text += f'\n{video_url}'
    for key, value in scopes.items():
        text = text.replace(key, value)
    return text


async def build_channel_data(bot: neocord.Bot, channel_id: str):
    _, info = await fetch_channel_info(channel_id, bot.session)
    _, latest_uploaded = await fetch_latest_uploaded(channel_id, bot.session)
    _, current_stream = await fetch_current_livestream(channel_id, bot.session)
    data = info
    if current_stream:
        data['live'] = {'url': current_stream["url"], 'id': current_stream["id"]}
    if latest_uploaded:
        data['upload'] = {'url': latest_uploaded["url"], 'id': latest_uploaded["id"]}
    return data


async def process(
        bot: neocord.Bot,
        *,
        event: str,
        channel_id: str,
        scanned_data: dict,
        channel_data: dict,
        guild: discord.Guild,
        entire_cache: dict,
        receiver: discord.TextChannel,
) -> str:
    logger = bot.get_channel(902228501120290866)
    channel_name = scanned_data.get('name')
    description = f'{Emo.SEARCH} **{channel_name}**\n'
    current_id = scanned_data[event]['id']
    stored_id = channel_data[channel_id][event]
    if not scanned_data.get(event):
        if event == "live":
            description += f'\n**{Emo.WARN} Channel is not live now**'
            return description
        elif event == "upload":
            description += f'\n**{Emo.WARN} Channel did not upload anything**'
            return description

    if not (current_id != stored_id):
        if event == "live":
            description += f'\n**{Emo.WARN} No new stream found**'
            return description
        elif event == "upload":
            description += f'\n**{Emo.WARN} No new upload found**'
            return description

    url = scanned_data[event]['url']
    channel_data[channel_id][event] = current_id
    try:
        await bot.db.add_field(str(guild.id), Field('CHANNELS', channel_data))
    except Exception as e:
        await log_exception(logger, guild, e)
    else:
        content = await custom_message(event, guild, channel_name, url, entire_cache)
        mention = await create_ping(guild, entire_cache) or ''
        if not content:
            if event == 'live':
                content = f'> {Emo.LIVE} **{channel_name}** is live now \n> {mention} {url}'
            else:
                content = f'> {Emo.YT} **{channel_name}** uploaded a new video\n> {mention} {url}'
        try:
            await receiver.send(content)
        except Exception as e:
            if not (isinstance(e, discord.errors.Forbidden) or isinstance(e, discord.errors.NotFound)):
                await log_exception(logger, guild, e)
        else:
            if event == 'live':
                description += (
                    f'\n**{Emo.LIVE} Channel is live now**'
                    f'\nNotification sent to: {receiver.mention}'
                    f'\n> {event.capitalize()} URL: {url}'
                )
            else:
                description += (
                    f'\n**{Emo.YT} Channel uploaded a new video**'
                    f'\nNotification sent to: {receiver.mention}'
                    f'> {event.capitalize()} URL: {url}'
                )
            return description


class ChannelSelectMenu(discord.ui.Select):
    def __init__(self, bot: neocord.Bot, ctx: neocord.Context, menu: list):
        self.bot = bot
        self.ctx = ctx
        super().__init__(min_values=1, max_values=1, options=menu, placeholder='existing youtube channels')

    async def callback(self, interaction: discord.Interaction):
        if not (interaction.user == self.ctx.author):
            return interaction.response.send_message('You are not the author of this command', ephemeral=True)
        await interaction.response.defer()
        channel_id = self.values[0]
        description = ''
        await self.ctx.edit_response(
            embed=discord.Embed(description=f'{Emo.SEARCH} Scanning in progress...'), view=None
        )

        data = await self.bot.db.get(str(interaction.guild.id)) or {}
        if not data.get('CHANNELS'):
            return await self.ctx.edit_response('No channels found.', embed=None, view=None)
        if not data['CHANNELS'][channel_id].get('receiver'):
            return await self.ctx.edit_response('No receiver found.', embed=None, view=None)

        channels = data['CHANNELS']
        saved_values = channels[channel_id]
        channel_data = await build_channel_data(self.bot, channel_id)
        receiver = await create_receiver(self.ctx.guild, channel_id, data)

        message = await process(
            self.bot,
            event="live",
            channel_id=channel_id,
            scanned_data=channel_data,
            channel_data=channels,
            guild=interaction.guild,
            entire_cache=data,
            receiver=receiver
        )
        await self.ctx.send_followup(embed=discord.Embed(description=message), ephemeral=True)

        message = await process(
            self.bot,
            event="upload",
            channel_id=channel_id,
            scanned_data=channel_data,
            channel_data=channels,
            guild=interaction.guild,
            entire_cache=data,
            receiver=receiver
        )
        await self.ctx.send_followup(embed=discord.Embed(description=message), ephemeral=True)


class Force(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    @neocord.cog.command(name='force', description='forces to check for new videos')
    async def force_check(self, ctx: neocord.Context):
        channels = self.bot.cached[ctx.guild.id].get('CHANNELS')
        await ctx.defer()
        if not channels:
            return await ctx.send_followup(
                embed=discord.Embed(description=f'> {Emo.WARN} no channel has been added yet'))
        menu = await create_menu(self.bot, list(channels))
        view = discord.ui.View()
        view.add_item(ChannelSelectMenu(self.bot, ctx, menu))
        embed = discord.Embed(description=f'> {Emo.YT} Select YouTube Channel to SCAN')
        await ctx.send_followup(embed=embed, view=view)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Force(bot))
