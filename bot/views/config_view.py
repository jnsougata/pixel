import io
import aiotube
import discord
from bot.extras.emojis import Emo
from app_util import Context, Bot


async def sub_view_config(bot: Bot, ctx: Context, value: int):

    if value == 0:
        data = bot.cached[ctx.guild.id].get('CHANNELS')
        if data:

            def make_channel_list():
                info = []
                for key, dict_value in data.items():
                    try:
                        channel = aiotube.Channel(key)
                        info.append(f'{Emo.TEXT} <#{dict_value["receiver"]}> {Emo.YT} [{channel.name}]({channel.url})')
                    except Exception:
                        info.append(f'{Emo.TEXT} <#1> {Emo.YT} [null](https://www.youtube.com/watch?v=iik25wqIuFo)')
                return info

            values = await bot.loop.run_in_executor(None, make_channel_list)
            emd = discord.Embed(description='\n\n'.join(values))
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t subscribed to any channels yet!')

    elif value == 1:
        data = data = bot.cached[ctx.guild.id].get('RECEIVER')
        if data and data.isdigit():
            channel = ctx.guild.get_channel(int(data))
            emd = discord.Embed(
                title=f'{Emo.CHECK} Default Receiver',
                description=f'The current set default receiver channel is '
                            f'{channel.mention if channel else "`invalid`"}'
                            f'\nThis channel will be used by default to receive youtube notifications')
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any default receiver yet!')

    elif value == 2:
        data = data = bot.cached[ctx.guild.id].get('RECEPTION')
        if data and data.isdigit():
            channel = ctx.guild.get_channel(int(data))
            emd = discord.Embed(
                title=f'{Emo.CHECK} Reception Channel',
                description=f'The current set reception channel is {channel.mention if channel else "<#1>"}'
                            f'\nThis channel will be used to send welcome cards')
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any reception channel yet!')

    elif value == 3:
        data = data = bot.cached[ctx.guild.id].get('PINGROLE')
        if data and data.isdigit():
            role = ctx.guild.get_role(int(data))
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
        try:
            card = await bot.drive.download(f'covers/{ctx.guild.id}_card.png')
        except Exception:
            card = await bot.drive.download(f'covers/default_card.png')

        emd = discord.Embed(title=f'{Emo.CHECK} Welcome Card')
        emd.set_image(url=f'attachment://card.png')
        await ctx.send_followup(embed=emd, file=discord.File(io.BytesIO(card), filename='card.png'))

    elif value == 5:
        data = data = bot.cached[ctx.guild.id].get('CUSTOM')
        if data:
            emojis = [Emo.DEAL, Emo.YT, Emo.LIVE]
            scopes = ['welcome', 'upload', 'live']
            messages = [data.get(slot, None) for slot in scopes]
            zipped = zip(emojis, scopes, messages)
            embeds = [
                discord.Embed(
                    title=f'{emoji} {scope.capitalize()} Message',
                    description=f'```\n{message}\n```')
                for emoji, scope, message in zipped if message]

            await ctx.send_followup(embeds=embeds)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any custom messages yet!')
