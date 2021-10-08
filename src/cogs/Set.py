import asyncio
from PIL import Image
import urllib.request
from asynctube import Channel
from src.extras.func import *
from discord.ext import commands
from src.extras.emojis import Emo


class Set(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='set', invoke_without_command=True)
    async def set(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} Subcommand Missing {Emo.WARN}',
            description=f'**You can use following:**'
                        f'\n\n**`youtube`**'
                        f'\n- sets a YouTube channel to Alert'
                        f'\n\n**`prefix`**'
                        f'\n- sets a custom prefix for your server'
                        f'\n\n**`reception`**'
                        f'\n- sets text channel for welcome cards'
                        f'\n\n**`welcomecard`**'
                        f'\n- sets an image as welcome card'
                        f'\n\n**`receiver`**'
                        f'\n- sets an text channel for YouTube Alert',
            color=0x005aef
        )
        emd.set_footer(text=f'✅ Syntax: {prefix}set  [subcommand]')
        await ctx.send(embed=emd)


    @set.command(name='reception')
    @commands.has_guild_permissions(administrator=True)
    async def set_reception(self, ctx, channel: discord.TextChannel = None):

        if channel is None:

            def check(m):
                return m.author == ctx.author

            await ctx.send('**Mention text channel for welcome cards:**')
            try:
                reply = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                await ctx.send('**Bye! you took so long!**')
                return
            try:
                ch = reply.channel_mentions[0]
                await db_push_object(
                    guildId=ctx.guild.id,
                    item = [str(ch.id)],
                    key='welcome'
                )
                await ctx.send(
                    f'{Emo.CHECK} **Current reception channel is** {ch.mention}'
                )
            except:
                await ctx.send(f'{Emo.WARN} **Mention a text channel properly!**')

        else:

            try:
                await db_push_object(
                    guildId = ctx.guild.id,
                    item = [str(channel.id)],
                    key='welcome'
                )
                await ctx.send(
                    f'{Emo.CHECK} **Current welcome channel is** {channel.mention}'
                )
            except:
                await ctx.send(f'{Emo.WARN} **Mention a text channel properly!**')


    

    @set.command(name='welcomecard')
    @commands.has_guild_permissions(administrator=True)
    async def set_welcomecard(self, ctx, url: str = None):

        def check(m):
            return m.author == ctx.author

        if url is not None:
            try:
                response = urllib.request.urlopen(url)
                Image.open(response)
                await db_push_object(
                    guildId=ctx.guild.id,
                    item = [url],
                    key='cover'
                )
                await ctx.send(f"{Emo.CHECK} **Cover picture accepted**")
            except:
                await ctx.send(f"{Emo.WARN} URL is not acceptable")

        else:
            await ctx.send(
                '**Please give URL of an Image [min]700x300**:'
            )
            try:
                reply = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                await ctx.send('**Bye! you took so long!**')
                return
            try:
                response = urllib.request.urlopen(reply.content)
                Image.open(response)
                await db_push_object(
                    guildId=ctx.guild.id,
                    item = [reply.content],
                    key='cover'
                )
                await ctx.send(f"{Emo.CHECK} **Cover picture accepted**")
            except:
                await ctx.send(f"{Emo.WARN} **URL is not acceptable**")


    @set.command(name='receiver')
    @commands.has_guild_permissions(administrator=True)
    async def set_receiver(self, ctx, channel: discord.TextChannel = None):

        if channel is None:

            def check(m):
                return m.author == ctx.author

            await ctx.send(f'**Mention a text channel to receive YouTube Alerts:**')

            try:
                reply = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Bye! you took so long!')
                return

            chs = reply.channel_mentions
            if len(chs) > 0:
                await db_push_object(
                    guildId=ctx.guild.id,
                    item = [str(chs[0].id)],
                    key='alertchannel'
                )
                await ctx.send(f'{Emo.CHECK} {chs[0].mention} **has been added for YouTube Alerts!**')
            else:
                await ctx.send(f'{Emo.WARN} **Mention a text channel properly!**')

        else:
            try:
                await db_push_object(
                    guildId = ctx.guild.id,
                    item = [str(channel.id)],
                    key='alertchannel'
                )
                await ctx.send(f'{Emo.CHECK} {channel.mention} **has been added for YouTube Alerts!**')
            except:
                await ctx.send(f'{Emo.WARN} **Mention a text channel properly!**')


    @set.command(aliases=['yt', 'youtube'])
    @commands.has_guild_permissions(administrator=True)
    async def set_youtube(self, ctx, Id: str = None):

        async def set_handler(YouTubeId: str):
            channel = await Channel.fetch(YouTubeId)

            if channel.valid:

                channelId = channel.id
                url = channel.url
                latest = await channel.latest
                liveId = 'empty'

                emd = discord.Embed(
                    title=f'{Emo.CHECK} Channel Added',
                    description=f'**`Name`** [{channel.name}]({url})'
                                f'\n\n **`Subs`** {channel.subscribers}'
                                f'\n\n **`Latest Video`** [Tap Here]({latest.url})',
                    color=0xFF0000
                )
                emd.set_thumbnail(url= await channel.avatar_url)
                await ctx.send(embed=emd)

                old_data = await db_fetch_object(
                    guildId = ctx.guild.id,
                    key = 'youtube'
                )

                if old_data:
                    if len(old_data['item']) > 0:
                        raw = old_data['item']
                        raw[channelId] = {'live': liveId, 'upload': await latest.id}

                        await db_push_object(
                            guildId=ctx.guild.id,
                            item = raw,
                            key = 'youtube'
                        )
                    else:
                        empty = dict()
                        empty[channelId] = {'live': liveId, 'upload': await latest.id}
                        await db_push_object(
                            guildId = ctx.guild.id,
                            item = empty,
                            key = 'youtube'
                        )
                else:
                    empty = dict()
                    empty[channelId] = {'live': liveId, 'upload': await latest.id}
                    await db_push_object(
                        guildId = ctx.guild.id,
                        item = empty,
                        key = 'youtube'
                    )
            else:
                emd = discord.Embed(
                    title=f'{Emo.WARN} Channel Not Found',
                    description=f'**`Name`** Not Found'
                                f'\n\n**`Subs`** Not Found'
                                f'\n\n**`Latest Video`** Not Found',
                    color=0xf5c20a
                )
                await ctx.send(embed=emd)

        receiver = await db_fetch_object(
            guildId = ctx.guild.id,
            key = 'alertchannel'
        )

        if receiver and len(receiver['item']) > 0:

            if Id is None:

                def check(m):
                    return m.author == ctx.author

                await ctx.send(f'**Type YouTube Channel Id / URL:**')

                try:
                    reply = await self.bot.wait_for('message', timeout=20, check=check)
                except asyncio.TimeoutError:
                    await ctx.send('Bye! you took so long!')
                    return

                await set_handler(reply.content)

            else:
                await set_handler(Id)

        else:
            prefix = await prefix_fetcher(ctx.guild.id)
            await ctx.send(
                f'{Emo.WARN} **Please add a text channel to receive YouTube Alert!**'
                f'\n**Use command** **` {prefix}set receiver `**'
            )

    @set.command(aliases=['prefix'])
    @commands.has_guild_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str = None):

        if prefix is None:
            def check(m):
                return m.author == ctx.author

            await ctx.send('**Enter custom Prefix:**')
            try:
                response = await self.bot.wait_for('message', check=check, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send('Bye! you took so long!')
                return
            if 0 < len(response.content) <= 3:
                await db_push_object(
                    guildId = ctx.guild.id,
                    item = [response.content],
                    key = 'prefix'
                )
                await ctx.send(
                    f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s new prefix is** `{response.content}`'
                )
            else:
                await ctx.send(
                    f'{Emo.WARN} **Please try with 3 or less characters!**'
                )
        else:
            if 0 < len(prefix) <= 3:
                await db_push_object(
                    guildId=ctx.guild.id,
                    item = [prefix],
                    key='prefix'
                )
                await ctx.send(
                    f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s new prefix is** `{prefix}`'
                )
            else:
                await ctx.send(
                    f'{Emo.WARN} **Please try with 3 or less characters!**'
                )


def setup(bot):
    bot.add_cog(Set(bot))