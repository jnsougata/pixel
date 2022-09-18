import neocord
import asyncio
import discord
import traceback
from deta import Field
from extras.emoji import Emo
from extras.utils import create_menu, fetch_latest_uploaded, fetch_current_livestream, fetch_channel_info


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
    data = {"info": info}
    if current_stream:
        data['stream'] = {'url': current_stream["url"], 'id': current_stream["id"]}
    if latest_uploaded:
        data['upload'] = {'url': latest_uploaded["url"], 'id': latest_uploaded["id"]}
    return data


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
        logger = self.bot.get_channel(938059433794240523)
        data = await self.bot.db.get(str(interaction.guild.id)) or {}
        if not data.get('CHANNELS'):
            return await self.ctx.edit_response('No channels found.', embed=None, view=None)
        if not data['CHANNELS'][channel_id].get('receiver'):
            return await self.ctx.edit_response('No receiver found.', embed=None, view=None)
        channels = data['CHANNELS']
        saved_values = channels[channel_id]
        mention = await create_ping(self.ctx.guild, data)
        receiver = await create_receiver(self.ctx.guild, channel_id, data)
        if not receiver:
            return await self.ctx.edit_response('No receiver found.', embed=None, view=None)
        channel_data = await build_channel_data(self.bot, channel_id)
        channel_name = channel_data['info']['name']
        description = f'Result for: {Emo.SEARCH} **{channel_name}**\n'

        if channel_data.get('stream'):
            old_live_id = saved_values['live']
            live_id = channel_data['stream']['id']
            live_url = channel_data['stream']['url']
            if old_live_id != live_id:
                message = await custom_message('live', self.ctx.guild, channel_name, live_url, data)
                if message:
                    c = message
                elif mention:
                    c = f'> {Emo.LIVE} **{channel_name}** is live now \n> {mention} {live_url}'
                else:
                    c = f'> {Emo.LIVE} **{channel_name}** is live now \n> {live_url}'
                try:
                    await receiver.send(c)
                except Exception as e:
                    if isinstance(e, discord.errors.Forbidden):
                        pass
                    else:
                        await self.log_exception(logger, guild, e)
                else:
                    description += f'\n{Emo.CHECK} **Streaming new live video**\n> URL: {live_url}\n'
                finally:
                    channels[channel_id]['live'] = live_id
            else:
                description += f'\n**{Emo.WARN} No new stream found**'
        else:
            description += f'\n**{Emo.WARN} Channel is not live**'

        if channel_data.get('upload'):
            old_latest_id = saved_values['upload']
            latest_id = channel_data['upload']['id']
            latest_url = channel_data['upload']['url']
            if latest_id != old_latest_id:
                message = await custom_message('upload', self.ctx.guild, channel_name, latest_url, data)
                if message:
                    c = message
                elif mention:
                    c = f'> {Emo.YT} **{channel_name}** uploaded a new video \n> {mention} {latest_url}'
                else:
                    c = f'> {Emo.YT} **{channel_name}** uploaded a new video \n> {latest_url}'
                try:
                    await receiver.send(c)
                except Exception as e:
                    if isinstance(e, discord.errors.Forbidden):
                        pass
                    else:
                        await self.log_exception(logger, guild, e)
                else:
                    description += f'\n{Emo.CHECK} **Uploaded a new video**\n> URL: {latest_url}\n'
                finally:
                    channels[channel_id]['upload'] = latest_id
            else:
                description += f'\n**{Emo.WARN} No new video uploaded**'
        else:
            description += f'\n**{Emo.WARN} Channel has no uploaded videos**'
        try:
            await self.bot.db.add_field(str(self.ctx.guild.id), Field('CHANNELS', channels))
        except Exception as e:
            await log_exception(logger, self.ctx.guild, e)
        await self.ctx.edit_response(embed=discord.Embed(description=description))


class Override(neocord.cog):
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
        await ctx.send_followup(
            embed=discord.Embed(description=f'> {Emo.YT} Select YouTube Channel to SCAN'), view=view)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Override(bot))
