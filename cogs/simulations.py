import neocord
import discord
from extras.emoji import Emo


async def create_ping(guild: discord.guild, cache: dict):
    role_id = cache[guild.id].get('PINGROLE')
    if not (role_id and role_id.isdigit()):
        return None
    role = guild.get_role(int(role_id))
    if role and role == guild.default_role:
        return '@everyone'
    elif role:
        return role.mention


async def create_receiver(guild: discord.Guild, youtube_id: str, cache: dict):
    receiver_id = cache[guild.id]['CHANNELS'][youtube_id]['receiver']
    if not (receiver_id and receiver_id.isdigit()):
        return None
    return guild.get_channel(int(receiver_id))


async def custom_message(event: str, guild: discord.Guild, channel_name: str, video_url: str, cache: dict):
    ping = await create_ping(guild, cache)
    scopes = {'[ping]': ping if ping else '', '[name]': channel_name, '[url]': video_url}
    data = cache[guild.id].get('CUSTOM')
    if not (data and data.get(event)):
        return None
    text = data.get(event)
    if '[url]' not in text:
        text += f'\n{video_url}'
    for key, value in scopes.items():
        text = text.replace(key, value)
    return text


async def youtube_simulate(bot: neocord.Bot, ctx: neocord.Context, event_type: str):
    cache = bot.cached
    if not cache[ctx.guild.id].get('CHANNELS'):
        return await ctx.edit_response('Add a channel first to simulate', embed=None, view=None)

    channel_id, _ = list(cache[ctx.guild.id].get('CHANNELS').items())[0]

    if not cache[ctx.guild.id]['CHANNELS'][channel_id].get('receiver'):
        return await ctx.edit_response('No receiver found.', embed=None, view=None)

    mention = await create_ping(ctx.guild, cache)
    receiver = await create_receiver(ctx.guild, channel_id, cache)
    channel_name = "Placeholder"
    if not receiver:
        return await ctx.edit_response(
            f'{Emo.WARN} Can not simulate. No receiver found {Emo.WARN}', embed=None, view=None)

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
            await ctx.edit_response(f'**YouTube Livestream simulated at {receiver.mention}**', embed=None, view=None)

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
            await ctx.edit_response(f'**YouTube Upload Simulated at {receiver.mention}**', embed=None, view=None)


class Utils(neocord.cog):
    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(name='ping', description='shows the avg latency of the bot')
    async def ping(self, ctx: neocord.Context):
        await ctx.send_response(f'**Pong:** {round(self.bot.latency * 1000)}ms')

    @neocord.cog.default_permission(discord.Permissions.manage_guild)
    @neocord.cog.command(
        name='simulate', description='simulates notifications',
        options=[
            neocord.IntOption(
                name='scope', description='scope to simulate', required=True,
                choices=[
                    neocord.Choice('welcome card', 1),
                    neocord.Choice('youtube upload', 2),
                    neocord.Choice('youtube livestream', 3)
                ]
            )
        ]
    )
    async def simulate(self, ctx: neocord.Context, scope: int):
        if scope == 1:
            await ctx.send_response(f'**Simulating:** welcome card')
            self.bot.dispatch('member_join', ctx.author)
        elif scope == 2:
            await ctx.send_response(f'**Simulating:** youtube upload')
            await youtube_simulate(self.bot, ctx, 'upload')
        elif scope == 3:
            await ctx.send_response(f'**Simulating:** youtube livestream')
            await youtube_simulate(self.bot, ctx, 'live')


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Utils(bot))
