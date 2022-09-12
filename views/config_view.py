import discord
import asyncio
from extras.emoji import Emo
from neocord import Context, Bot
from extras.utils import fetch_channel_info


DEFAULT_URL = 'https://www.youtube.com/channel/'


async def sub_view_config(bot: Bot, ctx: Context, value: int):

    if value == 1:
        data = bot.cached[ctx.guild.id].get('CHANNELS')
        if not data:
            return ctx.send_followup('> 👀 you have not subscribed to any channels yet!')

        tasks = [fetch_channel_info(key, bot.session) for key in list(data)]
        infos = await asyncio.gather(*tasks)
        fragments = []
        for chan_id, info in infos:
            if info:
                fragments.append(
                    f'{Emo.TEXT} <#{data[chan_id]["receiver"]}> {Emo.YT} [{info["name"]}]({info["url"]})')
            else:
                fragments.append(f'{Emo.TEXT} <#1234567890> {Emo.YT} [____]({DEFAULT_URL + info["url"]})')

        emd = discord.Embed(description='\n\n'.join(fragments))
        await ctx.send_followup(embed=emd)

    elif value == 2:
        data = bot.cached[ctx.guild.id].get('RECEPTION')
        if not (data and data.isdigit()):
            return await ctx.send_followup('> 👀 you have not set welcomer yet!')
        channel = ctx.guild.get_channel(int(data))
        if not channel:
            return await ctx.send_followup('> 👀 welcomer is not properly configured!')
        try:
            card = await bot.drive.get(f'covers/{ctx.guild.id}_card.png')
        except:
            card = await bot.drive.get('covers/default_card.png')
        file = discord.File(card, filename='card.png')
        emd = discord.Embed(description=f'{Emo.CHECK} Welcomer bound to <#{data}> with the following image:')
        emd.set_image(url=f'attachment://card.png')
        await ctx.send_followup(embed=emd, file=file)

    elif value == 3:
        data = data = bot.cached[ctx.guild.id].get('PINGROLE')
        if not (data and data.isdigit()):
            return await ctx.send_followup('> 👀 you have not set ping role yet!')

        role = ctx.guild.get_role(int(data))
        if role == ctx.guild.default_role:
            mention = '@everyone'
        else:
            mention = role.mention if role else '<@&1>'
        emd = discord.Embed(
            title=f'{Emo.CHECK} Ping Role',
            description=f'Ping role is set to {mention}\nThis will be used to ping members with youtube notifications')
        await ctx.send_followup(embed=emd)

    elif value == 4:
        data = data = bot.cached[ctx.guild.id].get('CUSTOM')
        if not data:
            return await ctx.send_followup('> 👀 you have not set any custom messages yet!')
        emojis = [Emo.DEAL, Emo.YT, Emo.LIVE]
        scopes = ['welcome', 'upload', 'live']
        messages = [data.get(slot, None) for slot in scopes]
        description = f'{Emo.CHECK} **custom messages**\n'
        for emoji, scope, message in zip(emojis, scopes, messages):
            if message:
                description += f'\n{emoji} {scope.capitalize()} Message\n```fix\n{message}\n```'
        emd = discord.Embed(description=description)
        await ctx.send_followup(embed=emd)
