import asyncio
import discord
from bot.extras.emojis import *
from extslash.commands import ApplicationContext, Bot
from bot.extras.func import db_push_object, db_fetch_object


async def secondary_callback(ctx: ApplicationContext, bot: Bot, event: str, valid_scope: discord.Embed, value: int):
    raw_data = await db_fetch_object(ctx.guild.id, 'text')
    if raw_data:
        db_data = raw_data
    else:
        db_data = {}

    if value == 1:

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.edit_response(
            embeds=[
                valid_scope,
                discord.Embed(
                    description=f'> {Emo.CUSTOM} **Type custom msg using above formatting scopes:**')],
            view=None)
        try:
            resp = await bot.wait_for('message', check=check, timeout=300)
            await ctx.edit_response(embed=discord.Embed(
                title=f'{Emo.CHECK} Custom {event.capitalize()} Message Updated',
                description=f'> {resp.content}'))
            db_data[event] = resp.content
            await db_push_object(ctx.guild.id, db_data, 'text')
        except asyncio.TimeoutError:
            await ctx.edit_response(embeds=[discord.Embed(description='Bye! you took too long to respond!')])
    elif value == 2:
        db_data[event] = ''
        await db_push_object(ctx.guild.id, db_data, 'text')
        await ctx.edit_response(embed=discord.Embed(
            title=f'{Emo.WARN} Done!',
            description=f'> Removed custom **{event}** message'))
    elif value == 3:
        await ctx.delete_response()


class ActionView(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
        self.ctx = ctx
        super().__init__()
        self.value = None

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def remove(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 3
            self.stop()


async def sub_view_msg(ctx: ApplicationContext, bot: Bot, value: int):

    if value == 0:
        welcome_action = ActionView(ctx)
        emd = discord.Embed(
            title=f'{Emo.IMG} Welcome Message',
            description=f'**Formatting Scopes**'
                        f'\n\n> `[guild.name]` will be replaced with the server name'
                        f'\n> `[ping.member]` this will ping the member with the card'
                        f'\n> `[member.name]` will be replaced with the member name'
                        f'\n> `[member.mention]` will be replaced with the member mention'
                        f'\n\nTap **`Edit`** to create a custom welcome message')
        emd.set_footer(text='You can mention any text channel directly inside the custom message')
        new = await ctx.edit_response(embed=emd, view=welcome_action)
        await welcome_action.wait()
        await secondary_callback(ctx, bot, 'welcome', emd, welcome_action.value)

    elif value == 1:
        upload_actions = ActionView(ctx)
        emd = discord.Embed(
            title=f'{Emo.YT} YT Upload Message',
            description=f'**Formatting Scopes**'
                        f'\n\n> `[ping]` will be replaced with the  role ping'
                        f'\n> `[url]` will be replaced with youtube video url'
                        f'\n> `[name]` will be replaced with youtube channel name'
                        f'\n\nTap **`Edit`** to create a custom youtube upload message')
        emd.set_footer(text='You can mention any text channel directly inside the custom message')
        new = await ctx.edit_response(embed=emd, view=upload_actions)
        await upload_actions.wait()
        await secondary_callback(ctx, bot, 'upload', emd, upload_actions.value)

    elif value == 2:
        live_actions = ActionView(ctx)
        emd = discord.Embed(
            title=f'{Emo.LIVE} YT Live Message',
            description=f'**Formatting Scopes**'
                        f'\n\n> `[ping]` will be replaced with the  role ping'
                        f'\n> `[url]` will be replaced with youtube video url'
                        f'\n> `[name]` will be replaced with youtube channel name'
                        f'\n\nTap **`Edit`** to create a custom youtube live message')
        emd.set_footer(text='You can mention any text channel directly inside the custom message')
        new = await ctx.edit_response(embed=emd, view=live_actions)
        await live_actions.wait()
        await secondary_callback(ctx, bot, 'live', emd, live_actions.value)
