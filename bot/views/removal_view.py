import io
import asyncio
import aiotube
import discord
from asyncdeta import Field
from bot.extras.emojis import Emo
from app_util import Context, Bot


class OptionView(discord.ui.View):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        super().__init__()
        self.value = None

    @discord.ui.button(label='Welcome', style=discord.ButtonStyle.green, emoji=f'{Emo.IMG}')
    async def welcome(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Upload', style=discord.ButtonStyle.blurple, emoji=f'{Emo.YT}')
    async def upload(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Live', style=discord.ButtonStyle.red, emoji=f'{Emo.LIVE}')
    async def live(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author == interaction.user:
            self.value = 3
            self.stop()

    async def on_timeout(self) -> None:
        pass


async def create_menu(loop: asyncio.AbstractEventLoop, channel_ids: list):

    def get_channel_names():
        return [aiotube.Channel(channel_id).name or 'EMPTY' for channel_id in channel_ids]

    channel_names = await loop.run_in_executor(None, get_channel_names)

    return [
               discord.SelectOption(label=name, value=id_, emoji=Emo.YT)
               for name, id_ in zip(channel_names, channel_ids)
           ][:24]


class ChannelMenu(discord.ui.Select):
    def __init__(self, bot, ctx: Context, menu: list):
        self.bot = bot
        self.ctx = ctx
        super().__init__(min_values=1, max_values=1, options=menu, placeholder='existing youtube channels')

    async def callback(self, interaction: discord.Interaction):
        channel_id = self.values[0]
        if interaction.user == self.ctx.author:
            if channel_id == '0':
                await self.ctx.delete_response()
                return
            ch = aiotube.Channel(channel_id)
            info = ch.info
            emd = discord.Embed(
                title=f'{Emo.WARN} {info["name"]}',
                description=f'\n> **Subs:** {info["subscribers"]}'
                            f'\n> **Views:** {info["views"]}'
                            f'\n> **Id:** {info["id"]}',
                url=info["url"],
                color=0xc4302b)
            banner_url = info['banner']
            avatar_url = info['avatar']
            if banner_url and banner_url.startswith('http'):
                emd.set_image(url=banner_url)
            if avatar_url and avatar_url.startswith('http'):
                emd.set_thumbnail(url=avatar_url)
            await self.ctx.edit_response(embed=emd, view=None)
            data = self.bot.cached[self.ctx.guild.id].get('CHANNELS')
            try:
                data.pop(channel_id)
            except KeyError:
                pass
            await self.bot.db.add_field(key=str(self.ctx.guild.id), field=Field('CHANNELS', data), force=True)


async def sub_view_remove(bot: Bot, ctx: Context, value: int):

    if value == 0:

        data = bot.cached[ctx.guild.id].get('CHANNELS')

        if data:
            menu = await create_menu(ctx.client.loop, list(data))
            menu.insert(0, discord.SelectOption(label='\u200b', value='0', emoji=Emo.CROSS))
            view = discord.ui.View()
            view.add_item(ChannelMenu(bot, ctx, menu))
            await ctx.send_followup(
                embed=discord.Embed(description='> Please select a channel from menu below:'),
                view=view)
        else:
            await ctx.send_followup(embed=discord.Embed(description='> There is no channel to remove.'))

    elif value == 1:
        bot.cached[ctx.guild.id]['RECEIVER'] = None
        await ctx.send_followup(embed=discord.Embed(description='> Default notification channel has been removed.'))
        await bot.db.add_field(key=str(ctx.guild.id), field=Field('RECEIVER', None), force=True)

    elif value == 2:
        bot.cached[ctx.guild.id]['RECEPTION'] = None
        await ctx.send_followup(embed=discord.Embed(description='> Welcome message channel has been removed.'))
        await bot.db.add_field(key=str(ctx.guild.id), field=Field('RECEPTION', None), force=True)

    elif value == 3:
        bot.cached[ctx.guild.id]['PINGROLE'] = None
        await ctx.send_followup(embed=discord.Embed(description='> Ping role has been removed.'))
        await bot.db.add_field(key=str(ctx.guild.id), field=Field('PINGROLE', None), force=True)

    elif value == 4:

        def delete_card():
            try:
                drive.delete(f'covers/{ctx.guild.id}_card.png')
            except:
                pass
        await bot.loop.run_in_executor(None, delete_card)
        await ctx.send_followup(embed=discord.Embed(description='> Welcome Card has been removed.'))

    elif value == 5:

        data = bot.cached[ctx.guild.id].get('CUSTOM')

        if data:
            view = OptionView(ctx)
            emd = discord.Embed(description='> Tap a button to remove corresponding message:')
            await ctx.send_followup(embed=emd, view=view)
            await view.wait()
            if view.value == 1:
                data['welcome'] = None
                await bot.db.add_field(key=str(ctx.guild.id), field=Field('CUSTOM', data), force=True)
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Welcome message has been removed.'), view=None)

            elif view.value == 2:
                data['upload'] = None
                await bot.db.add_field(key=str(ctx.guild.id), field=Field('CUSTOM', data), force=True)
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Upload message has been removed.'), view=None)

            elif view.value == 3:
                data['live'] = None
                await bot.db.add_field(key=str(ctx.guild.id), field=Field('CUSTOM', data), force=True)
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Live message has been removed.'), view=None)
        else:
            await ctx.send_followup('> 👀 you haven\'t set any custom messages yet!')
