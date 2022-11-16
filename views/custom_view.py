import neocord
import discord
from deta import Field
from extras.emoji import *


for_welcome = (
    '[guild.name] will be replaced with name of the Guild'
    '\n[member.name] will be replaced with name of the Member'
    '\n[member.mention] will mention the member inside the embed'
    '\n[ping.member] will ping the member with their welcome card'
)

for_youtube = (
    '[ping] will be replaced with Role Ping'
    '\n[url] will be replaced with the Video URL'
    '\n[name] will be replaced with the Channel NAME'
)

value_list = [for_welcome, for_youtube]


async def send_form(ctx: neocord.Context, bot: neocord.Bot, *, option_value: int, event: str, data: dict):
    prefilled = value_list[option_value]
    modal = neocord.Modal(title=f'{event.capitalize()} Message')
    modal.add_field(
        label='See Editing Scopes Here',
        style=neocord.TextFieldLength.LONG,
        custom_id='scopes',
        required=False,
        max_length=500,
        default_text=prefilled,
    )
    modal.add_field(
        label='Type Here',
        style=neocord.TextFieldLength.LONG,
        custom_id='message',
        hint='Type your custom message using the above scopes',
        required=True,
        max_length=2000,
        min_length=10,
    )
    await ctx.send_modal(modal)

    @modal.callback(bot)
    async def on_submit(mcx: neocord.Modal, scopes: str, message: str):
        embed = discord.Embed(
            title=f'{Emo.CHECK} {event.capitalize()} Message Updated',
            description=f'**Edited:**\n```{message}```'
        )
        await mcx.send_response(embed=embed)
        data[event] = message
        bot.cached[ctx.guild.id]['CUSTOM'] = data
        await bot.db.add_field(str(ctx.guild.id), Field('CUSTOM', data))


async def sub_view_msg(bot: neocord.Bot, ctx: neocord.Context, value: int):
    data = bot.cached[ctx.guild.id].get('CUSTOM') or {}
    if value == 0:
        await send_form(ctx, bot, option_value=value, event='welcome', data=data)
    elif value == 1:
        await send_form(ctx, bot, option_value=value, event='youtube', data=data)
