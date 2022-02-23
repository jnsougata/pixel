import io
import aiotube
import discord
import asyncio
from bot.extras.emojis import Emo
from app_util import Context
from bot.extras.func import db_fetch_object, drive


async def sub_view_config(value: int, ctx: Context):

    if value == 0:
        data = await db_fetch_object(ctx.guild.id, 'receivers')
        if data:
            def get_values():
                info = []
                for key, value in data.items():
                    yt_channel = aiotube.Channel(key)
                    info.append(f'[{yt_channel.name}]({yt_channel.url})\n\u200b■ <#{value}>')
                return info
            loop = asyncio.get_event_loop()
            values = await loop.run_in_executor(None, get_values)
            emd = discord.Embed(title=f'{Emo.YT} Subscriptions', description='\n\n'.join(values))
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t subscribed to any channels yet!')

    elif value == 1:
        data = await db_fetch_object(ctx.guild.id, 'alertchannel')
        if data and data[0].isdigit():
            channel = ctx.guild.get_channel(int(data[0]))
            emd = discord.Embed(
                title=f'{Emo.CHECK} Default Receiver',
                description=f'The current set default receiver channel is '
                            f'{channel.mention if channel else "`invalid`"}'
                            f'\nThis channel will be used by default to receive youtube notifications')
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any default receiver yet!')

    elif value == 2:
        data = await db_fetch_object(ctx.guild.id, 'welcome')
        if data and data[0].isdigit():
            channel = ctx.guild.get_channel(int(data[0]))
            emd = discord.Embed(
                title=f'{Emo.CHECK} Reception Channel',
                description=f'The current set reception channel is {channel.mention if channel else "<#1>"}'
                            f'\nThis channel will be used to send welcome cards')
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any reception channel yet!')

    elif value == 3:
        data = await db_fetch_object(ctx.guild.id, 'arole')
        if data and data[0].isdigit():
            role = ctx.guild.get_role(int(data[0]))
            if role == ctx.guild.default_role:
                mention = '@everyone'
            else:
                mention = role.mention if role else '<@&1>'
            emd = discord.Embed(
                title=f'{Emo.CHECK} Ping Role',
                description=f'Ping role is set to {mention}'
                            f'\nThis will be used to ping members with youtube notifications')
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any ping role yet!')

    elif value == 4:
        def form_cache():
            try:
                chunks = drive.cache(f'covers/{ctx.guild.id}_card.png')
            except Exception:
                chunks = drive.cache(f'covers/default_card.png')
            return io.BytesIO(chunks)
        loop = asyncio.get_event_loop()
        content = loop.run_in_executor(None, form_cache)
        emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card')
        emd.set_image(url=f'attachment://card.png')
        await ctx.send_followup(embed=emd, file=discord.File(await content, filename='card.png'))

    elif value == 5:
        data = await db_fetch_object(ctx.guild.id, 'text')
        if data:
            slots = ['welcome', 'upload', 'live']
            all_info = [f"**{slot.capitalize()}** ```\n{data.get(slot, 'None')}\n```"[:1000] + '...'
                        for slot in slots]
            emd = discord.Embed(title=f'{Emo.CHECK} Custom Messages', description='\n\n'.join(all_info))
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any custom messages yet!')
