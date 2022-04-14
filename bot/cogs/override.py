import discord
import app_util
from aiotube import Channel
from bot.extras.emojis import Emo
from bot.extras.func import db_push_object, db_fetch_object


async def check(ctx: app_util.Context):

    def check():
        p = ctx.channel.permissions_for(ctx.me)
        return p.send_messages and p.embed_links and p.attach_files and p.external_emojis

    if not ctx.guild:
        await ctx.send_response('🚫 This command can only be used inside a **SERVER**')
    elif not ctx.author.guild_permissions.manage_guild:
        await ctx.send_response('> 👀  You are not an **Admin** or **Server Manager**')
    elif not check():
        await ctx.send_response(
            f'> 😓  Please make sure I have permissions to send `embeds` `custom emojis` `attachments`')
    elif not ctx.options:
        await ctx.send_response('> 👀  you must select at least one option')
    else:
        return True


class Override(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.before_invoke(check_handler=check)
    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='force',
            description='forces to check for new videos',
            options=[app_util.StrOption(name='url', description='youtube channel url to check', required=True)]
        ),
    )
    async def force_check(self, ctx: app_util.Context, url: str):

        base_string = ''

        await ctx.defer()

        # helper funcs
        async def create_receiver(guild: discord.Guild, youtube_id: str):
            custom = await db_fetch_object(guild_id=guild.id, key='receivers')
            default = await db_fetch_object(guild_id=guild.id, key='alertchannel')
            if custom and custom.get(youtube_id):
                channel_id = custom.get(youtube_id)
                return guild.get_channel(int(channel_id))
            elif default and default[0].isdigit():
                return guild.get_channel(int(default[0]))
            return None

        async def create_ping(guild: discord.guild):
            data = await db_fetch_object(guild_id=guild.id, key='arole')
            if data and data[0].isdigit():
                role = guild.get_role(int(data[0]))
                if role and role == guild.default_role:
                    return '@everyone'
                elif role:
                    return role.mention
                return None

        async def custom_message(event: str, guild: discord.Guild, channel_name: str, video_url: str):
            ping = await create_ping(guild)
            scopes = {'[ping]': ping if ping else '', '[name]': channel_name, '[url]': video_url}
            text_dict = await db_fetch_object(guild_id=guild.id, key='text')
            if text_dict and text_dict.get(event):
                text = text_dict.get(event)
                for key, value in scopes.items():
                    text = text.replace(key, value)
                return text

        try:
            ch = Channel(url)
            info = ch.info
            channel_id = info['id']
            channel_name = info['name']
        except Exception:
            await ctx.send_followup(f'{Emo.WARN} entered **invalid** youtube channel url or id')
        else:
            base_string += f'\n{Emo.CHECK} checking for new videos in **{channel_name}**'
            fl = await ctx.send_followup(base_string)
            data = await db_fetch_object(guild_id=ctx.guild.id, key='youtube')
            if data and data.get(channel_id):
                receiver = await create_receiver(ctx.guild, channel_id)
                if receiver:
                    mention = await create_ping(ctx.guild)
                    try:
                        if ch.live:
                            live = ch.livestream
                            live_url = live.url
                            live_id = live.id
                            if data[channel_id]['live'] != live_id:
                                base_string += f'\n{Emo.LIVE} found new livestream: {live_url}'
                                await fl.edit(base_string)
                                try:
                                    message = await custom_message('live', ctx.guild, channel_name, live_url)
                                    if message:
                                        content = message
                                        await receiver.send(message)
                                    else:
                                        if mention:
                                            content = f'> {Emo.LIVE} **{ch.name}** is live now \n> {mention} {live_url}'
                                        else:
                                            content = f'> {Emo.LIVE} **{ch.name}** is live now \n> {live_url}'
                                except Exception:
                                    base_string += f'\n{Emo.WARN} Failed to send livestream notification' \
                                                   f'\nPlease check your server configuration' \
                                                   f'\n\n** This notification will not be sent again ** \n\n{live_url}'
                                    await fl.edit(base_string)
                                finally:
                                    data[channel_id]['live'] = live_id
                            else:
                                base_string += f'\n{Emo.LIVE} new livestream **NOT FOUND**'
                                await fl.edit(base_string)
                        else:
                            base_string += f'\n{Emo.CHECK} channel is currently **NOT LIVE**'
                            await fl.edit(base_string)

                        latest = ch.recent_uploaded
                        if latest:
                            latest_id = latest.id
                            latest_url = latest.url
                            if latest_id != data[channel_id]['upload']:
                                base_string += f'\n{Emo.YT} found new upload: {latest_url}'
                                await fl.edit(base_string)
                                message = await custom_message('upload', ctx.guild, channel_name, latest_url)
                                if message:
                                    content = message
                                else:
                                    if mention:
                                        content = f'> {Emo.YT} **{ch.name}** uploaded a new video \n> {mention} {latest_url}'
                                    else:
                                        content = f'> {Emo.YT} **{ch.name}** uploaded a new video \n> {latest_url}'
                                try:
                                    await receiver.send(content)
                                except Exception:
                                    base_string += f'\n{Emo.WARN} Failed to send upload notification'\
                                        f'\nPlease check your sever configuration'\
                                        f'\n\n** This notification will not be sent again **\n\n{latest_url}'
                                    await fl.edit(base_string)
                                finally:
                                    data[channel_id]['upload'] = latest_id
                                    await db_push_object(guild_id=ctx.guild.id, item=data, key='youtube')
                            else:
                                base_string += f'\n{Emo.CHECK} new upload **NOT FOUND**'
                                await fl.edit(base_string)
                        await db_push_object(guild_id=ctx.guild.id, item=data, key='youtube')
                    except Exception:
                        base_string += f'\n{Emo.WARN} something unexpected occurred!'
                        await fl.edit(base_string)
                else:
                    base_string += f'\n{Emo.WARN} I didn\'t find any receiver!'
                    await fl.edit(base_string)
            else:
                await fl.edit(f'{Emo.WARN} this youtube channel doesn\'t belong to this server!')


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Override(bot))
