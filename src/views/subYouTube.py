import discord
import asyncio
from aiotube import Channel
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_push_object, db_fetch_object, prefix_fetcher


class ChannelMenu(discord.ui.Select):

    @classmethod
    async def create(
            cls,
            ctx: commands.Context,
            bot: discord.Client,
    ):
        raw = await db_fetch_object(
            guild_id=ctx.guild.id,
            key='youtube'

        )
        if raw:
            ids = list(raw['item'])
            names = [Channel(id).name for id in list(raw['item'])]
            options = [
                discord.SelectOption(
                    label=names[i],
                    value=ids[i],
                    emoji=Emo.YT
                ) for i in range(len(ids))
            ]
            options.insert(
                0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS)
            )
        else:
            options = [
                discord.SelectOption(
                    label='Please add a channel',
                    emoji=Emo.WARN
                )
            ]
            options.insert(
                0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS)
            )
        return cls(
            options=options,
            context=ctx,
            bot=bot
        )

    def __init__(
            self,
            context: commands.Context,
            bot: discord.Client,
            options: list = None,
    ):
        self.ctx = context
        self.bot = bot

        super().__init__(
            placeholder='Search results',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if self.values[0] != '0':
                ch = Channel(self.values[0])
                data = ch.info
                emd = discord.Embed(
                    title=f'{Emo.DEL} {data["name"]}',
                    description=f'**` Subs `  {data["subscribers"]}**'
                                f'\n\n**` Views `  {data["views"]}**'
                                f'\n\n**` Id `  {data["id"]}**',
                    url=data["url"]
                )
                if data["avatar_url"] and data["banner_url"]:
                    emd.set_thumbnail(url=data["avatar_url"])
                    emd.set_image(url=data["banner_url"])
                emd.set_footer(text='❌ This channel has been removed.')
                await interaction.message.edit(
                    embed=emd,
                    view=None
                )
                db_raw = await db_fetch_object(
                    guild_id=self.ctx.guild.id,
                    key='youtube'
                )
                new_data = db_raw['item']
                new_data.pop(self.values[0])

                await db_push_object(
                    guild_id=self.ctx.guild.id,
                    item=new_data,
                    key='youtube'
                )
            else:
                await interaction.message.delete()


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot
        super().__init__()
        self.value = None

    @discord.ui.button(label='Add', style=discord.ButtonStyle.green)
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 0
            self.stop()


class Confirmation(discord.ui.View):
    def __init__(self, ctx: commands.Context, bot: discord.Client):
        self.ctx = ctx
        self.message = None
        self.bot = bot
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = False
            self.stop()


class Temp(discord.ui.View):
    def __init__(self):
        self.message = None
        super().__init__()


async def sub_view_youtube(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    raw = await db_fetch_object(
        guild_id=ctx.guild.id,
        key='alertchannel'
    )

    def _check():
        if raw['item'] and raw['item'][0].isdigit():
            return ctx.guild.get_channel(int(raw['item'][0]))

    if raw and _check():
        emd = discord.Embed(
            description=f'**{ctx.guild.name}\'s** YouTube channel Settings'
                        f'\n\nTo add new channel tap **` Add `**'
                        f'\n\nTo remove old channel tap **` Remove `**'
        )
        if ctx.guild.icon:
            emd.set_author(
                icon_url=ctx.guild.icon.url,
                name=ctx.guild.name
            )
        else:
            emd.set_author(
                icon_url=ctx.guild.me.avatar.url,
                name=ctx.guild.me.name
            )
        view = Option(ctx, bot)
        await interaction.response.edit_message(embed=emd, view=view)
        await view.wait()

        if view.value == 2:
            view = Temp()
            view.add_item(await ChannelMenu.create(ctx, bot))
            await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description='Please select YouTube Channel to **remove:**'
                ),
                view=view
            )
        elif view.value == 1:
            view.clear_items()
            new = await interaction.message.edit(
                content=f'{ctx.author.mention}',
                embed=discord.Embed(
                    description='Please **type** a youtube channel **ID** or **URL:**'
                ),
                view=view
            )

            def check(m):
                return m.author == ctx.author

            try:
                response = await bot.wait_for('message', check=check, timeout=20)
                channel = Channel(response.content)
                try:
                    data = channel.info
                    emd = discord.Embed(
                            title=f'{Emo.YT} {data["name"]}',
                            description=f'**` Subs `  {data["subscribers"]}**'
                                        f'\n\n**` Views `  {data["views"]}**',
                            url=data["url"]
                    )
                    if data["avatar_url"] and data["banner_url"]:
                        emd.set_thumbnail(url=data["avatar_url"])
                        emd.set_image(url=data["banner_url"])

                    new_view = Confirmation(ctx, bot)
                    await new.delete()
                    nxt = await ctx.send(
                        content=f'{ctx.author.mention}',
                        embed=emd,
                        view=new_view
                    )
                    await new_view.wait()
                    if new_view.value is True:
                        old_data = await db_fetch_object(
                            guild_id=ctx.guild.id,
                            key='youtube'
                        )
                        if old_data:
                            raw = old_data['item']
                            raw[data['id']] = {'live': 'empty', 'upload': channel.latest.id}
                            await db_push_object(
                                guild_id=ctx.guild.id,
                                item=raw,
                                key='youtube'
                            )
                        else:
                            empty = dict()
                            empty[data['id']] = {'live': 'empty', 'upload': channel.latest.id}
                            await db_push_object(
                                guild_id=ctx.guild.id,
                                item=empty,
                                key='youtube'
                            )
                        await nxt.edit(
                            content=f'{Emo.CHECK} {ctx.author.mention} **YouTube Channel added successfully!**',
                            view=None
                        )
                    else:
                        await nxt.delete()
                except Exception:
                    await ctx.send(
                        embed=discord.Embed(
                            description=f'{Emo.WARN} Invalid YouTube Channel Id or URL'
                        )
                    )
                    await interaction.message.delete()

            except asyncio.TimeoutError:
                await ctx.send('**Bye! you took so long**')

        elif view.value == 0:
            await interaction.message.delete()

    else:
        p = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} No Receiver Found {Emo.WARN}',
            description=f'Please set a Text Channel '
                        f'\nfor receiving Livestream Notifications'
                        f'\n\n**`Steps`**'
                        f'\n**{p}setup**  select **receiver** from menu '
                        f'\nThen tap **Edit**  select **text channel** from menu'
        )
        await interaction.response.edit_message(embed=emd, view=None)
