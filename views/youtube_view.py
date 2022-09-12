import discord
import asyncio
from deta import Field
from extras.emojis import *
from neocord import Context, Bot
from extras.utils import fetch_channel_info, fetch_latest_uploaded, form_id


def has_perms(channel: discord.TextChannel, ctx: Context):
    bot_can = channel.permissions_for(ctx.me)
    return bot_can.send_messages and bot_can.embed_links and bot_can.use_external_emojis


async def check_receiver_perms(ctx: Context, receiver: discord.TextChannel):
    bot_can = receiver.permissions_for(ctx.me)
    if not bot_can.send_messages:
        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a receiver',
            description=f'I cannot set {receiver.mention} as receiver'
                        f'\nBecause I am unable to send messages in that channel'
        )
        await ctx.send_followup(embed=embed)
        return False
    elif not bot_can.embed_links:
        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a receiver',
            description=f'I cannot set {receiver.mention} as receiver'
                        f'\nBecause I am unable to embed links in that channel'
        )
        await ctx.send_followup(embed=embed)
        return False
    elif not bot_can.use_external_emojis:
        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a receiver',
            description=f'I cannot set {receiver.mention} as receiver'
                        f'\nBecause I am unable to use external emojis in that channel'
        )
        await ctx.send_followup(embed=embed)
        return False
    else:
        return True


async def sub_view_youtube(bot: Bot, ctx: Context, url: str, receiver: discord.TextChannel):
    if not await check_receiver_perms(ctx, receiver):
        return
    data = bot.cached[ctx.guild.id].get('CHANNELS')
    if data and not len(data) < 10:
        return await ctx.send_followup(
            embed=discord.Embed(description=f'{Emo.WARN} Exceeded the maximum allowed channels (10) {Emo.WARN}'))
    _, info = await fetch_channel_info(form_id(url), bot.session)
    if not info:
        return await ctx.send_followup(
            embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'))
    _, uploaded = await fetch_latest_uploaded(form_id(url), bot.session)
    content = {
        'live': 'empty',
        'upload': uploaded.get('id') or 'empty',
        'receiver': str(receiver.id)
    }
    if data:
        data[info['id']] = content
    else:
        data = {info['id']: content}
    await bot.db.add_field(key=str(ctx.guild.id), field=Field(name='CHANNELS', value=data), force=True)
    emd = discord.Embed(
        description=f'{Emo.YT} **[{info["name"]}]({info["url"]})**'
                    f'\n\n> **Subs:** {info["subscribers"]}\n> **Views:** {info["views"]}'
                    f'\n> **Bound to:** <#{receiver.id}>', color=0xc4302b)
    emd.set_footer(text=f'✅ channel added successfully by {ctx.author}'),
    banner_url = info.get('banner')
    avatar_url = info.get('avatar')
    if banner_url and banner_url.startswith('http'):
        emd.set_image(url=banner_url)
    if avatar_url and avatar_url.startswith('http'):
        emd.set_thumbnail(url=avatar_url)
    await ctx.send_followup(embed=emd)
