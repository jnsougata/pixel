import discord
import app_util
from bot.extras.emojis import *
from bot.extras.func import db_push_object, db_fetch_object

for_welcome = '''
[guild.name] => server name
[ping.member] => notify user
[member.name] => member name
[member.mention] => @mention user silently
'''
for_upload = '''
[ping] => role ping
[url] => youtube video url
[name] => youtube channel name'
'''

for_live = '''
[ping] => role ping
[url] => youtube video url
[name] => youtube channel name'
'''

value_list = [for_welcome, for_upload, for_live]


async def update_message(ctx: app_util.Context, bot: app_util.Bot, *, option_value: int, event: str, data: dict):
    prefilled = value_list[option_value]
    modal = app_util.Modal(client=bot, title=f'Custom Message')
    modal.add_field(
        label='See Editing Scopes Here',
        style=app_util.TextInputStyle.PARAGRAPH,
        custom_id='scopes',
        value=prefilled,
        required=False,
        max_length=500,
    )
    modal.add_field(
        label='Type Here',
        style=app_util.TextInputStyle.PARAGRAPH,
        custom_id='message',
        hint='Type your custom message using the above scopes...',
        required=True,
        max_length=2000,
        min_length=10,
    )
    await ctx.send_modal(modal)

    @modal.callback
    async def on_submit(mcx: app_util.Modal, scopes, message: str):
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
        await update_message(ctx, bot, option_value=value, event='welcome', data=db_data)
    elif value == 1:
        await update_message(ctx, bot, option_value=value, event='upload', data=db_data)
    elif value == 2:
        await update_message(ctx, bot, option_value=value, event='live', data=db_data)
