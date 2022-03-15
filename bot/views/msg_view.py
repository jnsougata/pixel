import discord
import app_util
from bot.extras.emojis import *
from bot.extras.func import db_push_object, db_fetch_object

for_welcome = '''For member name: [member.name]
For server name use: [guild.name]
To notify user use: [ping.member]
To mention user silently: [member.mention]'''

for_upload = '''To ping role use: [ping]
For upload url use: [url]
For channel name use: [name]'''

for_live = '''To ping role: [ping]
For livestream url: [url]
For channel name: [name]'''

value_list = [for_welcome, for_upload, for_live]


async def send_form(ctx: app_util.Context, bot: app_util.Bot, *, option_value: int, event: str, data: dict):
    prefilled = value_list[option_value]
    modal = app_util.Modal(client=bot, title=f'{event.capitalize()} Message')
    modal.add_field(
        label='See Editing Scopes Here',
        style=app_util.ModalTextType.LONG,
        custom_id='scopes',
        value=prefilled,
        required=False,
        max_length=500,
    )
    modal.add_field(
        label='Type Here',
        style=app_util.ModalTextType.LONG,
        custom_id='message',
        hint='Type your custom message using the above scopes',
        required=True,
        max_length=2000,
        min_length=10,
    )
    await ctx.send_modal(modal)

    @modal.callback
    async def on_submit(mcx: app_util.Modal, scopes: str, message: str):
        embed = discord.Embed(
            title=f'{Emo.CHECK} {event.capitalize()} Message Updated',
            description=f'**Edited:**\n```{message}```'
        )
        await mcx.send_response(embed=embed)
        data[event] = message
        await db_push_object(mcx.guild.id, data, 'text')


async def sub_view_msg(ctx: app_util.Context, value: int, bot: app_util.Bot):

    raw_data = await db_fetch_object(ctx.guild.id, 'text')
    if raw_data:
        db_data = raw_data
    else:
        db_data = {}
    if value == 0:
        await send_form(ctx, bot, option_value=value, event='welcome', data=db_data)
    elif value == 1:
        await send_form(ctx, bot, option_value=value, event='upload', data=db_data)
    elif value == 2:
        await send_form(ctx, bot, option_value=value, event='live', data=db_data)
