import app_util
import discord
from bot.extras.emojis import Emo
from aiotube import Channel
from bot.extras.func import db_push_object, db_fetch_object


class Override(app_util.Cog):
    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='force',
            description='forces to check for new videos',
            options=[
                app_util.StrOption(
                    name='url',
                    description='youtube channel url to check',
                    required=True
                )
            ]
        ),
    )
    async def force_check(self, ctx: app_util.Context):

        await ctx.defer(ephemeral=True)

        if not isinstance(ctx.author, discord.Member):
            await ctx.send_followup('🚫 This command can only be used inside a **SERVER**')
            return

        if not ctx.author.guild_permissions.administrator:
            await ctx.send_followup('> 👀  You are not an **Admin** or **Equivalent**')
            return

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
                    return role
                elif role:
                    return role.mention
                return None

        async def custom_message(event: str, guild: discord.Guild, channel_name: str, video_url: str):
            ping = await create_ping(guild)
            scopes = {
                '[ping]': ping if ping else '',
                '[name]': channel_name,
                '[url]': video_url,
            }
            text_dict = await db_fetch_object(guild_id=guild.id, key='text')
            if text_dict and text_dict.get(event):
                text = text_dict.get(event)
                for key, value in scopes.items():
                    text = text.replace(key, value)
                return text

        url = ctx.options['url'].value
        ch = Channel(url)

        try:
            channel_id = ch.id
            channel_name = ch.name
        except Exception:
            await ctx.send_followup(f'{Emo.WARN} entered invalid youtube channel url')
            return
        else:
            await ctx.send_followup(f'{Emo.CHECK} Checking for new videos in {channel_name}')

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
                            await ctx.send_followup(
                                f'{Emo.LIVE} Found new livestream: {live_url}'
                                f'\nSending notification...', ephemeral=True)
                            try:
                                message = await custom_message('live', ctx.guild, channel_name, live_url)
                                if message:
                                    await receiver.send(message)
                                else:
                                    if mention:
                                        await receiver.send(
                                            f'> {Emo.LIVE} **{ch.name}** is live now'
                                            f'\n> {mention} {live_url}')
                                    else:
                                        await receiver.send(
                                            f'> {Emo.LIVE} **{ch.name}** is live now'
                                            f'\n> {live_url}')
                            except Exception as e:
                                print(e)
                                await ctx.send_followup(f'{Emo.WARN} Failed to send notification'
                                                        f'\nPlease check your server configuration'
                                                        f'\n\n** This notification will not be sent again **')
                            finally:
                                data[channel_id]['live'] = live_id
                        else:
                            await ctx.send_followup(f'{Emo.LIVE} new livestream NOT FOUND', ephemeral=True)

                    latest = ch.recent_uploaded
                    if latest:
                        latest_id = latest.id
                        latest_url = latest.url
                        if latest_id != data[channel_id]['upload']:
                            await ctx.send_followup(
                                f'{Emo.YT} Found new upload: {latest_url}'
                                f'\nSending notification...', ephemeral=True)
                            try:
                                message = await custom_message('upload', ctx.guild, channel_name, latest_url)
                                if message:
                                    await receiver.send(message)
                                else:
                                    if mention:
                                        await receiver.send(
                                            f'> {Emo.YT} **{ch.name}** uploaded a new video'
                                            f'\n> {mention} {latest_url}')
                                    else:
                                        await receiver.send(
                                            f'> {Emo.YT} **{ch.name}** uploaded a new video'
                                            f'\n> {latest_url}')
                            except Exception as e:
                                print(e)
                                await ctx.send_followup(f'{Emo.WARN} Failed to send notification'
                                                        f'\nPlease check your sever configuration'
                                                        f'\n\n** This notification will not be sent again **')
                            finally:
                                data[channel_id]['upload'] = latest_id
                                await db_push_object(guild_id=ctx.guild.id, item=data, key='youtube')
                        else:
                            await ctx.send_followup(f'{Emo.YT} new upload NOT FOUND', ephemeral=True)

                    await db_push_object(guild_id=ctx.guild.id, item=data, key='youtube')

                except Exception:
                    await ctx.send_followup(f'{Emo.WARN} Something Unexpected Occurred!')
            else:
                await ctx.send_followup(f'{Emo.WARN} I didn\'t find any receiver!')
        else:
            await ctx.send_followup(f'{Emo.WARN} this youtube channel doesn\'t belong to this server!')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Override(bot))
