import aiotube
import asyncio
import discord
import app_util
import traceback
from asyncdeta import Field
from bot.extras.emojis import Emo


class ChannelSelectMenu(discord.ui.Select):
    def __init__(self, bot: app_util.Bot, ctx: app_util.Context, menu: list):
        self.bot = bot
        self.ctx = ctx
        super().__init__(min_values=1, max_values=1, options=menu, placeholder='existing youtube channels')

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            channel_id = self.values[0]
            target = aiotube.Channel(channel_id)
            await interaction.response.defer()
            response_embed_description = ''
            await self.ctx.edit_response(
                embed=discord.Embed(description=f'{Emo.SEARCH} Scanning in progress...'), view=None
            )

            # auxiliary functions
            async def create_ping(guild: discord.guild, _cache: dict):
                role_id = _cache[guild.id].get('PINGROLE')
                if role_id and role_id.isdigit():
                    role = guild.get_role(int(role_id))
                    if role and role == guild.default_role:
                        return '@everyone'
                    elif role:
                        return role.mention
                return None

            async def create_receiver(guild: discord.Guild, youtube_id: str, _cache: dict):
                try:
                    default_receiver_id = _cache[guild.id]['RECEIVER']
                    specific_receiver_id = _cache[guild.id]['CHANNELS'][youtube_id]['receiver']
                    if specific_receiver_id and specific_receiver_id.isdigit():
                        return guild.get_channel(int(specific_receiver_id))
                    elif default_receiver_id and default_receiver_id.isdigit():
                        return guild.get_channel(int(default_receiver_id))
                    return None
                except KeyError:
                    return None

            async def custom_message(
                    event: str, guild: discord.Guild, _channel_name: str, video_url: str, _cache: dict):
                ping = await create_ping(guild, cache)
                scopes = {'[ping]': ping if ping else '', '[name]': _channel_name, '[url]': video_url}
                data = _cache[guild.id].get('CUSTOM')
                if data and data.get(event):
                    text = data.get(event)
                    if '[url]' not in text:
                        text += f'\n{video_url}'
                    for key, value in scopes.items():
                        text = text.replace(key, value)
                    return text
                return None

            async def log_exception(channel: discord.TextChannel, guild: discord.Guild, error: Exception):
                stack = traceback.format_exception(type(error), error, error.__traceback__)
                tb = ''.join(stack)
                await channel.send(embed=discord.Embed(
                    title=f'Exception occurred during scaning',
                    description=f'**Guild: {guild.name} | ID: {guild.id}**\n```py\n{tb}\n```'))

            async def build_cached_data(guild: discord.Guild):
                entire_cache = await self.bot.db.fetch_all()
                for data in entire_cache:
                    if data['key'] == str(guild.id):
                        return {guild.id: data}

            logger = self.bot.get_channel(938059433794240523)
            cache = await build_cached_data(self.ctx.guild)
            if not cache[self.ctx.guild.id]['CHANNELS']:
                return await self.ctx.edit_response('No channels found.', embed=None, view=None)
            if not cache[self.ctx.guild.id]['CHANNELS'][target.id].get('receiver'):
                return await self.ctx.edit_response('No receiver found.', embed=None, view=None)

            channels = cache[self.ctx.guild.id]['CHANNELS']
            saved_values = channels[channel_id]
            mention = await create_ping(self.ctx.guild, cache)
            receiver = await create_receiver(self.ctx.guild, channel_id, cache)
            if receiver:
                channel_data = {}
                if target.livestream:
                    channel_data['stream'] = {'url': target.livestream.url, 'id': target.livestream.id}
                if target.recent_uploaded:
                    channel_data['upload'] = {'url': target.recent_uploaded.url, 'id': target.recent_uploaded.id}
                channel_data['info'] = target.info
                channel_name = channel_data['info']['name']
                response_embed_description = f'Result for: {Emo.SEARCH} **{channel_name}**\n'

                if channel_data.get('stream'):
                    live_url = channel_data['stream']['url']
                    live_id = channel_data['stream']['id']
                    old_live_id = saved_values['live']
                    if old_live_id != live_id:
                        message = await custom_message('live', self.ctx.guild, channel_name, live_url, cache)
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
                            response_embed_description += f'\n**Streaming new live video**\n>URL: {live_url}'
                        finally:
                            channels[channel_id]['live'] = live_id
                    else:
                        response_embed_description += f'\n**{Emo.WARN} No new livestream found**'
                else:
                    response_embed_description += f'\n**{Emo.WARN} Channel is not live**'

                if channel_data.get('upload'):
                    latest_id = channel_data['upload']['id']
                    latest_url = channel_data['upload']['url']
                    old_latest_id = saved_values['upload']
                    if latest_id != old_latest_id:
                        message = await custom_message('upload', self.ctx.guild, channel_name, latest_url, cache)
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
                            response_embed_description += f'\n**Uploaded a new video**\n>URL: {latest_url}'
                        finally:
                            channels[channel_id]['upload'] = latest_id
                    else:
                        response_embed_description += f'\n**{Emo.WARN} No new video uploaded**'
                else:
                    response_embed_description += f'\n**{Emo.WARN} Channel has no uploaded videos**'
                try:
                    await self.bot.db.add_field(str(self.ctx.guild.id), Field('CHANNELS', channels), force=True)
                except Exception as e:
                    await log_exception(logger, self.ctx.guild, e)

            await self.ctx.edit_response(embed=discord.Embed(description=response_embed_description))


async def check(ctx: app_util.Context):

    p = ctx.channel.permissions_for(ctx.me)
    if not p.send_messages and p.embed_links and p.external_emojis:
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis`')
    else:
        return True


class Override(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.default_permission(discord.Permissions.manage_guild)
    @app_util.Cog.check(check)
    @app_util.Cog.command(command=app_util.SlashCommand(name='force', description='forces to check for new videos'))
    async def force_check(self, ctx: app_util.Context):

        async def create_menu(loop: asyncio.AbstractEventLoop, channel_ids: list):
            def get_channel_names():
                return [aiotube.Channel(channel_id).name or 'null' for channel_id in channel_ids]

            channel_names = await loop.run_in_executor(None, get_channel_names)

            return [
                       discord.SelectOption(label=name, value=id_, emoji=Emo.SEARCH)
                       for name, id_ in zip(channel_names, channel_ids)
                   ][:10]

        menu = await create_menu(self.bot.loop, self.bot.cached[ctx.guild.id].get('CHANNELS'))
        view = discord.ui.View()
        view.add_item(ChannelSelectMenu(self.bot, ctx, menu))
        await ctx.send_response(
            embed=discord.Embed(description=f'> {Emo.YT} Select YouTube Channel to SCAN'),
            view=view)


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Override(bot))
