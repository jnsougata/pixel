import io
import aiotube
import discord
import asyncio
from bot.extras.emojis import Emo
from extslash.commands import ApplicationContext, Bot
from bot.extras.func import db_fetch_object, drive, db_push_object, drive


async def create_menu(data: dict, loop: asyncio.AbstractEventLoop):
    channel_ids = list(data)

    def get_channel_names():
        return [aiotube.Channel(id_).name for id_ in channel_ids]
    channel_names = await loop.run_in_executor(None, get_channel_names)
    return [discord.SelectOption(label=name, value=id_, emoji=Emo.YT)
            for name, id_ in zip(channel_names, channel_ids)]


class ChannelMenu(discord.ui.Select):
    def __init__(self, ctx: ApplicationContext, menu: list):
        self.ctx = ctx
        super().__init__(min_values=1, max_values=1, options=menu, placeholder='existing channels')


    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if self.values[0] == '0':
                await self.ctx.delete_response()
                return
            ch = aiotube.Channel(self.values[0])
            info = ch.info
            emd = discord.Embed(
                description=f'{Emo.CROSS} [{info["name"]}]({info["url"]})'
                            f'\n**Subs:** {info["subscribers"]}'
                            f'\n**Views:** {info["views"]}'
                            f'\n**Id:** {info["id"]}',
                color=0xc4302b)
            banner_url = info.get('banner_url')
            avatar_url = info.get('avatar_url')
            if banner_url and banner_url.startswith('http'):
                emd.set_image(url=banner_url)
            if avatar_url and avatar_url.startswith('http'):
                emd.set_thumbnail(url=avatar_url)
            await self.ctx.edit_response(embed=emd, view=None)
            yt_data = await db_fetch_object(guild_id=self.ctx.guild.id, key='youtube')
            rc_data = await db_fetch_object(guild_id=self.ctx.guild.id, key='receivers')
            yt_data.pop(self.values[0])
            rc_data.pop(self.values[0])
            await db_push_object(guild_id=self.ctx.guild.id, item=yt_data, key='youtube')
            await db_push_object(guild_id=self.ctx.guild.id, item=rc_data, key='receivers')


async def sub_view_remove(ctx: ApplicationContext, value: int):

    if value == 0:
        data = await db_fetch_object(ctx.guild.id, 'receivers')
        if data:
            loop = asyncio.get_event_loop()
            menu = await create_menu(data, loop)
            menu.insert(0, discord.SelectOption(label='\u200b', value='0', emoji=Emo.CROSS))
            view = discord.ui.View()
            view.add_item(ChannelMenu(ctx, menu))
            await ctx.send_followup(
                embed=discord.Embed(description='> Please select a channel from menu below:'),
                view=view)
        else:
            await ctx.send_followup(embed=discord.Embed(description='> There is no channel to remove.'))

    elif value == 1:
        await db_push_object(ctx.guild.id, ['removed'], 'alertchannel')
        await ctx.send_followup(embed=discord.Embed(description='> Default notification channel has been removed.'))

    elif value == 2:
        await db_push_object(ctx.guild.id, ['removed'], 'welcome')
        await ctx.send_followup(embed=discord.Embed(description='> Welcome message channel has been removed.'))

    elif value == 3:
        await db_push_object(ctx.guild.id, ['removed'], 'arole')
        await ctx.send_followup(embed=discord.Embed(description='> Ping role has been removed.'))

    elif value == 4:
        loop = asyncio.get_event_loop()

        def remove_card():
            try:
                drive.delete(f'covers/{ctx.guild.id}_card.png')
            finally:
                return
        await loop.run_in_executor(None, remove_card)
        await ctx.send_followup(embed=discord.Embed(description='> Welcome Card has been removed.'))

    elif value == 5:
        data = await db_fetch_object(ctx.guild.id, 'text')

        if data:

            class OptionView(discord.ui.View):
                def __init__(self, ctx: ApplicationContext):
                    self.ctx = ctx
                    self.timeout = 60
                    super().__init__()
                    self.value = None

                @discord.ui.button(label='Welcome', style=discord.ButtonStyle.green, emoji=f'{Emo.IMG}')
                async def welcome(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.ctx.author == interaction.user:
                        self.value = 1
                        self.stop()

                @discord.ui.button(label='Upload', style=discord.ButtonStyle.blurple, emoji=f'{Emo.YT}')
                async def upload(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.ctx.author == interaction.user:
                        self.value = 2
                        self.stop()

                @discord.ui.button(label='Live', style=discord.ButtonStyle.red, emoji=f'{Emo.LIVE}')
                async def live(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.ctx.author == interaction.user:
                        self.value = 3
                        self.stop()

                async def on_timeout(self) -> None:
                    pass

            view = OptionView(ctx)
            emd = discord.Embed(description='> Tap a button to remove corresponding msg:')
            await ctx.send_followup(embed=emd, view=view)
            await view.wait()
            if view.value == 1:
                data['welcome'] = None
                await db_push_object(ctx.guild.id, data, 'text')
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Welcome message has been removed.'), view=None)

            elif view.value == 2:
                data['upload'] = None
                await db_push_object(ctx.guild.id, data, 'text')
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Upload message has been removed.'), view=None)

            elif view.value == 3:
                data['live'] = None
                await db_push_object(ctx.guild.id, data, 'text')
                await ctx.edit_response(
                    embed=discord.Embed(description='> Custom Live message has been removed.'), view=None)

        else:
            await ctx.send_followup('> 👀 you haven\'t set any custom messages yet!')
