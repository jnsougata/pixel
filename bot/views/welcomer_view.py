import discord
import asyncio
import aiohttp
from asyncdeta import Field
from bot.extras.emojis import *
from extlib import Context, Bot


async def sub_view_welcomer(bot: Bot, ctx: Context, image: discord.Attachment, reception: discord.TextChannel):

    async def check_reception_perms():
        bot_can = reception.permissions_for(ctx.me)
        if not bot_can.send_messages:
            embed = discord.Embed(
                title=f'{Emo.WARN} I cannot set that as a reception',
                description=f'I cannot set {reception.mention} as reception'
                            f'\nBecause I am unable to `send messages` in that channel'
            )
            await ctx.edit_response(embed=embed)
            return False

        elif not bot_can.attach_files:
            embed = discord.Embed(
                title=f'{Emo.WARN} I cannot set that as a reception',
                description=f'I cannot set {reception.mention} as reception'
                            f'\nBecause I am unable to `attach files` in that channel'
            )
            await ctx.send_followup(embed=embed)
            return False
        else:
            return True

    if reception and image:
        if await check_reception_perms():
            await bot.db.add_field(key=str(ctx.guild.id), field=Field('RECEPTION', str(reception.id)), force=True)
            emd = discord.Embed(
                title=f'{Emo.CHECK} Welcome Card Updated',
                description=f'Bound to <#{reception.id}>',
            )
            emd.set_image(url=image.url)
            await ctx.send_followup(embed=emd)

            bot.cached[ctx.guild.id]['RECEPTION'] = str(reception.id)

            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as resp:
                    chunks = await resp.read()
                    await bot.drive.upload(file_name=f'covers/{ctx.guild.id}_card.png', content=chunks)
    elif reception:
        if await check_reception_perms():
            await bot.db.add_field(key=str(ctx.guild.id), field=Field('RECEPTION', str(reception.id)), force=True)
            emd = discord.Embed(
                title=f'{Emo.CHECK} Reception Updated',
                description=f'Current set reception channel is {reception.mention}'
                            f'\nThis channel will be used to send welcome cards')
            await ctx.send_followup(embed=emd)

            bot.cached[ctx.guild.id]['RECEPTION'] = str(reception.id)
