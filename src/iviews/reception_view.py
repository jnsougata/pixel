import discord
from src.extras.emojis import *
from extslash.commands import ApplicationContext, Bot
from src.extras.func import db_push_object, db_fetch_object


class BaseView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None
        self.timeout = 180

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


class TextMenu(discord.ui.Select):

    def __init__(self, ctx: ApplicationContext, bot: Bot):
        self.ctx = ctx
        self.bot = bot
        channels = ctx.guild.text_channels
        eligible = [channel for channel in channels if channel.permissions_for(ctx.guild.me).attach_files]
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id), emoji=Emo.TEXT) for channel in eligible[:24]
        ]
        options.insert(
            0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
        )
        super().__init__(
            placeholder='Select a text channel',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) != 0:
                channel = self.bot.get_channel(int(self.values[0]))
                emd = discord.Embed(
                    title=f'{Emo.CHECK} Reworked',
                    description=f'Current set reception channel is {channel.mention}'
                                f'\nThis channel will be used to send welcome cards')
                await self.ctx.edit_response(embed=emd, view=None)
                await db_push_object(guild_id=self.ctx.guild.id, item=[self.values[0]], key='welcome')
            else:
                await self.ctx.delete_response()


async def sub_view_reception(ctx: ApplicationContext, bot: Bot):

    raw = await db_fetch_object(guild_id=ctx.guild.id, key='welcome')

    def _check():
        if raw and raw[0].isdigit():
            reception = ctx.guild.get_channel(int(raw[0]))
            try:
                return reception.mention
            except AttributeError:
                return '**`None`**'
        else:
            return '**`None`**'

    emd = discord.Embed(
        description=f'**{ctx.guild.name}\'s** current reception is {_check()}'
                    f'\n\nTo set new reception tap **`Edit`**'
                    f'\n\n{Emo.WARN} Only accepts text channels where'
                    f'\nit has permission to send **Attachments** and **Embeds**')
    emd.set_author(icon_url=ctx.me.avatar.url, name=ctx.me.name)
    view = Option(ctx)
    await ctx.edit_response(embed=emd, view=view)
    await view.wait()

    if view.value == 1:
        new_view = BaseView()
        new_view.add_item(TextMenu(ctx, bot))
        await ctx.edit_response(embed=discord.Embed(
            description=f'> {Emo.DEAL} Please **select** a text channel to use as **Reception:**'),
            view=new_view)
    elif view.value == 2:
        await ctx.edit_response(
            embed=discord.Embed(description=f'{Emo.DEL} Reception removed'), view=None)
        await db_push_object(guild_id=ctx.guild.id, item=['removed'], key='welcome')
    elif view.value == 0:
        await ctx.delete_response()
