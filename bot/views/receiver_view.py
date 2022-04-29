import discord
from asyncdeta import Field
from bot.extras.emojis import *
from app_util import Context, Bot


async def sub_view_receiver(bot: Bot, ctx: Context, channel: discord.TextChannel):

    bot_can = channel.permissions_for(ctx.me)

    if not bot_can.send_messages:

        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a reception',
            description=f'I cannot set the reception as {channel.mention}'
                        f'\nBecause I am unable to send messages in that channel'
        )
        await ctx.edit_response(embed=embed)

    elif not bot_can.embed_links:

        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a reception',
            description=f'I cannot set the receiver as {channel.mention}'
                        f'\nBecause I am unable to embed links in that channel'
        )
        await ctx.edit_response(embed=embed)

    else:
        emd = discord.Embed(
            title=f'{Emo.CHECK} Receiver Updated',
            description=f'The current set default receiver is {channel.mention}'
                        f'\nThis channel will be used by default for notifications')
        await ctx.edit_response(embed=emd)

        bot.cached[ctx.guild.id]['RECEIVER'] = str(channel.id)
        await bot.db.add_field(key=str(ctx.guild.id), field=Field('RECEIVER', str(channel.id)), force=True)
