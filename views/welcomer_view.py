import discord
import aiohttp
from deta import Field
from extras.emoji import *
from neocord import Context, Bot


async def check_reception_perms(ctx: Context, reception: discord.TextChannel):
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


async def sub_view_welcomer(bot: Bot, ctx: Context, image: discord.Attachment, reception: discord.TextChannel):

    if reception and image:
        if not await check_reception_perms(ctx, reception):
            return
        await bot.db.add_field(str(ctx.guild.id), Field('RECEPTION', str(reception.id)))
        emd = discord.Embed(
            title=f'{Emo.CHECK} Welcome Card Updated',
            description=f'Bound to <#{reception.id}>',
        )
        emd.set_image(url=image.url)
        await ctx.send_followup(embed=emd)
        bot.cached[ctx.guild.id]['RECEPTION'] = str(reception.id)
        content = await image.read()
        await bot.drive.upload(content, f'covers/{ctx.guild.id}_card.png')

    elif reception:
        if not await check_reception_perms(ctx, reception):
            return
        await bot.db.add_field(str(ctx.guild.id), Field('RECEPTION', str(reception.id)))
        emd = discord.Embed(
            title=f'{Emo.CHECK} Reception Updated',
            description=f'Current set reception channel is {reception.mention}'
                        f'\nThis channel will be used to send welcome cards')
        await ctx.send_followup(embed=emd)
        bot.cached[ctx.guild.id]['RECEPTION'] = str(reception.id)
