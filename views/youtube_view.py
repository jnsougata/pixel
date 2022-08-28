import discord
import asyncio
import aiotube
import aiotube.errors
from deta import Field
from extras.emojis import *
from neocord import Context, Bot


def has_perms(channel: discord.TextChannel, ctx: Context):
    bot_can = channel.permissions_for(ctx.me)
    return bot_can.send_messages and bot_can.embed_links and bot_can.use_external_emojis


async def sub_view_youtube(bot: Bot, ctx: Context, url: str, receiver: discord.TextChannel):

    async def check_receiver_perms():
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

    if await check_receiver_perms():
        old_data = bot.cached[ctx.guild.id].get('CHANNELS')
        if old_data:
            total_channels = len(old_data)
        else:
            total_channels = 0

        if total_channels <= 9:
            try:
                channel = aiotube.Channel(url)
                info = channel.info
            except (aiotube.errors.InvalidURL, aiotube.errors.AIOError):
                await ctx.send_followup(
                    embed=discord.Embed(description=f'{Emo.WARN} Invalid YouTube Channel ID or URL'))
            except aiotube.errors.TooManyRequests:
                await ctx.send_followup(
                    embed=discord.Embed(
                        description=f'{Emo.WARN} you are requesting too often, try again in a few seconds'))
            except Exception as e:
                await ctx.send_followup(
                    embed=discord.Embed(description=f'{Emo.WARN} Unusual error. Your url is probably invalid'))
            else:
                await asyncio.sleep(1.5)
                upload = channel.recent_uploaded
                upload_id = upload.id if upload else None
                if old_data:
                    bot.cached[ctx.guild.id]['CHANNELS'][info['id']] = {
                        'live': 'empty', 'upload': upload_id or 'empty'
                    }
                else:
                    bot.cached[ctx.guild.id]['CHANNELS'] = {
                        info['id']: {'live': 'empty', 'upload': upload_id or 'empty'}
                    }

                bot.cached[ctx.guild.id]['CHANNELS'][info['id']]['receiver'] = str(receiver.id)

                await bot.db.add_field(
                    key=str(ctx.guild.id),
                    field=Field(name='CHANNELS', value=bot.cached[ctx.guild.id]['CHANNELS']),
                    force=True
                )
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
        else:
            await ctx.send_followup(
                embed=discord.Embed(
                    description=f'{Emo.WARN} Exceeded the maximum allowed channels (10) {Emo.WARN}'))
