import asyncio
import discord
from deta import Field
from extras.emoji import Emo
from neocord import Context, Bot
from extras.utils import fetch_channel_info, create_menu


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


class ChannelMenu(discord.ui.Select):
    def __init__(self, bot: Bot, ctx: Context, menu: list):
        self.bot = bot
        self.ctx = ctx
        super().__init__(
            min_values=1,
            max_values=1,
            options=menu,
            placeholder='existing youtube channels'
        )

    async def callback(self, interaction: discord.Interaction):
        if not (interaction.user == self.ctx.author):
            return
        await interaction.response.defer()
        channel_id = self.values[0]
        if channel_id == '0':
            await self.ctx.delete_response()
            return
        _, info = await fetch_channel_info(channel_id, self.bot.session)
        emd = discord.Embed(
            title=f'🚮 {info["name"]}',
            description=(
                f'\n> **Subs:** {info["subscribers"]}'
                f'\n> **Views:** {info["views"]}'
                f'\n> **Id:** {info["id"]}'
            ),
            url=info["url"], color=0xc4302b)
        emd.set_image(url=info.get('banner'))
        emd.set_thumbnail(url=info.get('avatar'))
        await self.ctx.edit_response(embed=emd, view=None)
        try:
            self.bot.cached[self.ctx.guild.id].get('CHANNELS').pop(channel_id)
        except KeyError:
            pass
        else:
            await self.bot.db.add_field(
                self.ctx.guild.id,
                Field('CHANNELS', self.bot.cached[self.ctx.guild.id].get('CHANNELS')),
            )


async def sub_view_remove(bot: Bot, ctx: Context, value: int):

    if value == 1:
        data = bot.cached[ctx.guild.id].get('CHANNELS')
        if not data:
            return await ctx.send_followup(embed=discord.Embed(description='> There is no channel to remove.'))
        menu = await create_menu(bot, list(data))
        menu.insert(0, discord.SelectOption(label='cancel', value='0', emoji=Emo.CROSS))
        view = discord.ui.View()
        view.add_item(ChannelMenu(bot, ctx, menu))
        await ctx.send_followup(
            embed=discord.Embed(description='> Please select a channel from menu below:'), view=view)

    elif value == 2:
        bot.cached[ctx.guild.id]['RECEPTION'] = None
        await ctx.send_followup(embed=discord.Embed(description='> Welcomer has been removed.'))
        await bot.db.add_field(str(ctx.guild.id), Field('RECEPTION', None))

    elif value == 3:
        bot.cached[ctx.guild.id]['PINGROLE'] = None
        await ctx.send_followup(embed=discord.Embed(description='> Ping role has been removed.'))
        await bot.db.add_field(str(ctx.guild.id), Field('PINGROLE', None))

    elif value == 4:
        data = bot.cached[ctx.guild.id].get('CUSTOM')
        if not data:
            return await ctx.send_followup('> 👀 you have not set any custom messages yet!')
        view = OptionView(ctx)
        emd = discord.Embed(description='> Tap a button to remove corresponding message:')
        await ctx.send_followup(embed=emd, view=view)
        await view.wait()

        if view.value == 1:
            data['welcome'] = None
            await bot.db.add_field(str(ctx.guild.id), Field('CUSTOM', data))
            await ctx.edit_response(
                embed=discord.Embed(description='> Custom Welcome message has been removed.'), view=None)

        elif view.value == 2:
            data['upload'] = None
            await bot.db.add_field(str(ctx.guild.id), Field('CUSTOM', data))
            await ctx.edit_response(
                embed=discord.Embed(description='> Custom Upload message has been removed.'), view=None)

        elif view.value == 3:
            data['live'] = None
            await bot.db.add_field(str(ctx.guild.id), Field('CUSTOM', data))
            await ctx.edit_response(
                embed=discord.Embed(description='> Custom Live message has been removed.'), view=None)
