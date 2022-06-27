import io
import aiotube
import discord
from disfix import Context, Bot
from bot.extras.emojis import Emo


async def sub_view_config(bot: Bot, ctx: Context, value: int):

    if value == 1:
        data = bot.cached[ctx.guild.id].get('CHANNELS')
        if data:

            def make_channel_list():
                info = []
                for key, dict_value in data.items():
                    try:
                        channel_ = aiotube.Channel(key)
                        info.append(
                            f'{Emo.TEXT} <#{dict_value["receiver"]}> {Emo.YT} [{channel_.name}]({channel_.url})')
                    except Exception:
                        info.append(f'{Emo.TEXT} <#1> {Emo.YT} [null](https://www.youtube.com/watch?v=iik25wqIuFo)')
                return info

            values = await bot.loop.run_in_executor(None, make_channel_list)
            emd = discord.Embed(description='\n\n'.join(values))
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you haven\'t subscribed to any channels yet!')

    elif value == 2:
        data = bot.cached[ctx.guild.id].get('RECEPTION')
        if data and data.isdigit():
            channel = ctx.guild.get_channel(int(data))
            if channel:
                try:
                    card = await bot.drive.get(f'covers/{ctx.guild.id}_card.png')
                except:
                    card = await bot.drive.get('covers/default_card.png')
                file = discord.File(card, filename='card.png')
                emd = discord.Embed(description=f'{Emo.CHECK} Welcomer bound to <#{data}> with the following card:')
                emd.set_image(url=f'attachment://card.png')
                await ctx.send_followup(embed=emd, file=file)
            else:
                await ctx.send_followup('> 👀 welcomer is not properly configured!')
        else:
            await ctx.send_followup('> 👀 you have not set welcomer yet!')

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
        data = data = bot.cached[ctx.guild.id].get('CUSTOM')
        if data:
            emojis = [Emo.DEAL, Emo.YT, Emo.LIVE]
            scopes = ['welcome', 'upload', 'live']
            messages = [data.get(slot, None) for slot in scopes]
            zipped = zip(emojis, scopes, messages)
            description = f'{Emo.CHECK} **custom messages**\n'
            for emoji, scope, message in zipped:
                if message:
                    description += f'\n{emoji} {scope.capitalize()} Message\n```fix\n{message}\n```'

            emd = discord.Embed(description=description)
            await ctx.send_followup(embed=emd)
        else:
            await ctx.send_followup('> 👀 you have not set any custom messages yet!')
