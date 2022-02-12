import io
import aiotube
import discord
import asyncio
from bot.extras.func import db_fetch_object, drive
from bot.extras.emojis import Emo
from extslash.commands import ApplicationContext


async def handle_configs(value: int, ctx: ApplicationContext):

    if value == 0:
        data = await db_fetch_object(ctx.guild.id, 'receivers')
        if data:
            def main():
                info = []
                for key, value in data.items():
                    yt_channel = aiotube.Channel(key)
                    txt = ctx.guild.get_channel(int(value))
                    info.append(f'{txt.mention if txt else "<#1>"} ([{yt_channel.name}]({yt_channel.url}))')
                return info
            loop = asyncio.get_event_loop()
            all_info = loop.run_in_executor(None, main)
            emd = discord.Embed(title=f'{Emo.YT} Subscriptions', description='\n\n'.join(await all_info))
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
        def cache():
            try:
                chunks = drive.cache(f'covers/{ctx.guild.id}_card.png')
            except Exception:
                chunks = drive.cache(f'covers/default_card.png')
            return io.BytesIO(chunks)
        loop = asyncio.get_event_loop()
        content = loop.run_in_executor(None, cache)
        emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card')
        emd.set_image(url=f'attachment://card.png')
        await ctx.send_followup(embed=emd, file=discord.File(await content, filename='card.png'))

    elif value == 5:
        data = await db_fetch_object(ctx.guild.id, 'text')
        if data:
            slots = ['welcome', 'upload', 'live']
            all_info = [f"**`{slot.capitalize()} Message`**\n↳ {data.get(slot, '..........(default)')}"
                        for slot in slots]
            emd = discord.Embed(title=f'{Emo.CHECK} Custom Messages', description='\n\n'.join(all_info))
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any custom messages yet!')
