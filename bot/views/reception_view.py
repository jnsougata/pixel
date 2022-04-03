import discord
from bot.extras.emojis import *
from app_util import Context, Bot
from bot.extras.func import db_push_object, db_fetch_object


async def sub_view_reception(ctx: Context, channel: discord.TextChannel):

    bot_can = channel.permissions_for(ctx.me)
    
    if not bot_can.send_messages:
        
        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a reception',
            description=f'I cannot set the reception as {channel.mention}'
                        f'\nBecause I am unable to send messages in that channel'
        )
        await ctx.edit_response(embed=embed)

    elif not bot_can.attach_files:

        embed = discord.Embed(
            title=f'{Emo.WARN} I cannot set that as a reception',
            description=f'I cannot set the receiver as {channel.mention}'
                        f'\nBecause I am unable to attach files in that channel'
        )
        await ctx.edit_response(embed=embed)

    else:
        emd = discord.Embed(
            title=f'{Emo.CHECK} Reception Updated',
            description=f'Current set reception channel is {channel.mention}'
                        f'\nThis channel will be used to send welcome cards')
        await ctx.edit_response(embed=emd)
        await db_push_object(guild_id=ctx.guild.id, item=[str(channel.id)], key='welcome')
