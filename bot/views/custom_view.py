import discord
import extlib
from asyncdeta import Field
from bot.extras.emojis import *


for_welcome = '''For member name use: [member.name]
For server name use: [guild.name]
To notify user use: [ping.member]
To mention user silently use: [member.mention]'''

for_upload = '''To ping role use: [ping]
For upload url use: [url]
For channel name use: [name]'''

for_live = '''To ping role use: [ping]
For livestream url use: [url]
For channel name use: [name]'''

value_list = [for_welcome, for_upload, for_live]


async def send_form(ctx: extlib.Context, bot: extlib.Bot, *, option_value: int, event: str, data: dict):
    prefilled = value_list[option_value]
    modal = extlib.Modal(title=f'{event.capitalize()} Message')
    modal.add_field(
        label='See Editing Scopes Here',
        style=extlib.ModalTextType.LONG,
        custom_id='scopes',
        required=False,
        max_length=500,
        default_text=prefilled,

    )
    modal.add_field(
        label='Type Here',
        style=extlib.ModalTextType.LONG,
        custom_id='message',
        hint='Type your custom message using the above scopes',
        required=True,
        max_length=2000,
        min_length=10,
    )
    await ctx.send_modal(modal)

    @modal.callback(bot)
    async def on_submit(mcx: extlib.Modal, scopes: str, message: str):
        embed = discord.Embed(
            title=f'{Emo.CHECK} {event.capitalize()} Message Updated',
            description=f'**Edited:**\n```{message}```'
        )
        await mcx.send_response(embed=embed)
        data[event] = message
        bot.cached[ctx.guild.id]['CUSTOM'] = data
        await bot.db.add_field(key=str(ctx.guild.id), field=Field('CUSTOM', data), force=True)


async def sub_view_msg(bot: extlib.Bot, ctx: extlib.Context, value: int):

    old_data = bot.cached[ctx.guild.id].get('CUSTOM')
    data = old_data if old_data else {}
    if value == 0:
        await send_form(ctx, bot, option_value=value, event='welcome', data=data)
    elif value == 1:
        await send_form(ctx, bot, option_value=value, event='upload', data=data)
    elif value == 2:
        await send_form(ctx, bot, option_value=value, event='live', data=data)
