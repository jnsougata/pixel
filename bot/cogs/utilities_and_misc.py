import disfix
import discord
import aiotube
from bot.extras.emojis import Emo


async def youtube_simulate(bot: disfix.Bot, ctx: disfix.Context, event_type: str):
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

    async def custom_message(event: str, guild: discord.Guild, _channel_name: str, video_url: str, _cache: dict):
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
    cache = bot.cached
    if not cache[ctx.guild.id].get('CHANNELS'):
        return await ctx.edit_response('Add a channel first to simulate', embed=None, view=None)

    channel_id, _ = list(cache[ctx.guild.id].get('CHANNELS').items())[0]

    if not cache[ctx.guild.id]['CHANNELS'][channel_id].get('receiver'):
        return await ctx.edit_response('No receiver found.', embed=None, view=None)

    mention = await create_ping(ctx.guild, cache)
    receiver = await create_receiver(ctx.guild, channel_id, cache)
    channel_name = "Placeholder"
    if receiver:
        if event_type == "live":
            live_url = "https://www.youtube.com/watch?v=5qap5aO4i9A"
            message = await custom_message('live', ctx.guild, channel_name, live_url, cache)
            if message:
                c = message
            elif mention:
                c = f'> {Emo.LIVE} **{channel_name}** is live now \n> {mention} {live_url}'
            else:
                c = f'> {Emo.LIVE} **{channel_name}** is live now \n> {live_url}'
            try:
                await receiver.send(c)
            except Exception as e:
                await ctx.edit_response(f'{Emo.WARN} Failed to send livestream message.', embed=None, view=None)
            else:
                await ctx.edit_response(f'`YouTube Livestream simulated at` {receiver.mention}', embed=None, view=None)

        if event_type == "upload":
            latest_url = "https://www.youtube.com/watch?v=iik25wqIuFo"
            message = await custom_message('upload', ctx.guild, channel_name, latest_url, cache)
            if message:
                c = message
            elif mention:
                c = f'> {Emo.YT} **{channel_name}** uploaded a new video \n> {mention} {latest_url}'
            else:
                c = f'> {Emo.YT} **{channel_name}** uploaded a new video \n> {latest_url}'
            try:
                await receiver.send(c)
            except Exception as e:
                await ctx.edit_response(f'{Emo.WARN} Failed to send upload message.', embed=None, view=None)
            else:
                await ctx.edit_response(f'`YouTube Upload Simulated at` {receiver.mention}', embed=None, view=None)
    else:
        await ctx.edit_response(f'{Emo.WARN} Can not simulate. No receiver found {Emo.WARN}', embed=None, view=None)


class Utils(disfix.cog):
    def __init__(self, bot: disfix.Bot):
        self.bot = bot

    @disfix.cog.command(
        name='ping',
        description='shows the avg latency of the bot',
        guild_id=877399405056102431,
        category=disfix.CommandType.SLASH
    )
    async def ping_command(self, ctx: disfix.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @disfix.cog.command(
        name='simulate',
        description='simulates notifications',
        guild_id=877399405056102431,
        category=disfix.CommandType.SLASH,
        options=[
            disfix.IntOption(
                name='scope',
                description='scope to simulate',
                required=True,
                choices=[
                    disfix.Choice(name='welcome card', value=1),
                    disfix.Choice(name='youtube upload', value=2),
                    disfix.Choice(name='youtube livestream', value=3),
                ]
            )
        ]
    )
    async def simulate_command(self, ctx: disfix.Context, scope: int):
        if scope == 1:
            await ctx.send_response(f'**Simulating:** welcome card')
            self.bot.dispatch('member_join', ctx.author)
        elif scope == 2:
            await ctx.send_response(f'**Simulating:** youtube upload')
            await youtube_simulate(self.bot, ctx, 'upload')
        elif scope == 3:
            await ctx.send_response(f'**Simulating:** youtube livestream')
            await youtube_simulate(self.bot, ctx, 'live')


async def setup(bot: disfix.Bot):
    await bot.add_application_cog(Utils(bot))
