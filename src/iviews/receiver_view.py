import discord
from src.extras.emojis import *
from extslash.commands import ApplicationContext, Bot
from src.extras.func import db_push_object, db_fetch_object


class BaseView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None

    async def on_timeout(self) -> None:
        pass


class Option(discord.ui.View):
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
            self.value = 0
            self.stop()


class TextChannelMenu(discord.ui.Select):

    def __init__(self, ctx: ApplicationContext, bot: Bot):
        self.ctx = ctx
        self.bot = bot
        channels = ctx.guild.text_channels
        eligible = [channel for channel in channels if channel.permissions_for(ctx.me).embed_links]
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id), emoji=Emo.TEXT) for channel in eligible[:24]
        ]
        options.insert(
            0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
        )
        super().__init__(
            min_values=1,
            max_values=1,
            options=options,
            placeholder='Select a text channel',
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) != 0:
                channel = self.bot.get_channel(int(self.values[0]))
                emd = discord.Embed(
                    title=f'{Emo.CHECK} Reworked',
                    description=f'The current set default receiver channel is {channel.mention}'
                                f'\nThis channel will be used to receive livestream & upload notifications')
                await self.ctx.edit_response(embed=emd, view=None)
                await db_push_object(guild_id=self.ctx.guild.id, item=[self.values[0]], key='alertchannel')
            else:
                await self.ctx.delete_response()


async def sub_view_receiver(ctx: ApplicationContext, bot: Bot):

    raw = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')

    def _check():
        if raw and raw[0].isdigit():
            receiver = ctx.guild.get_channel(int(raw[0]))
            try:
                return receiver.mention
            except AttributeError:
                return '**`None`**'
        else:
            return '**`None`**'

    emd = discord.Embed(
        description=f'> To change default receiver tap **`Edit`**'
                    f'\n\n**{ctx.guild.name}\'s** current default receiver is {_check()}'
                    f'\n\n{Emo.WARN} Only accepts text channels with **embed links** permission'
                    f'\n\n{Emo.INFO} **Don\'t worry!**'
                    f'\nyou can always assign specific text channels for specific '
                    f'\nYouTube Channels once you have a default text channel assigned')
    emd.set_author(icon_url=ctx.me.avatar.url, name=ctx.me.name)
    view = Option(ctx)
    await ctx.edit_response(embed=emd, view=view)
    await view.wait()
    if view.value == 1:
        new_view = BaseView()
        new_view.add_item(TextChannelMenu(ctx, bot))
        await ctx.edit_response(
            embed=discord.Embed(description=f'> {Emo.PING} Please **select** a text channel to use as **Receiver:**'),
            view=new_view)
    elif view.value == 2:
        await ctx.edit_response(embed=discord.Embed(description=f'{Emo.DEL} Receiver removed'), view=None)
        await db_push_object(guild_id=ctx.guild.id, item=['removed'], key='alertchannel')
    elif view.value == 0:
        await ctx.delete_response()
