import sys
import asyncio
import discord
import traceback
from aiotube import Channel
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_fetch_object, db_push_object


class Temp(discord.ui.View):
    def __init__(self):
        self.message = None
        super().__init__()


class StreamerList(discord.ui.Select):

    @classmethod
    async def create(
            cls,
            ctx: commands.Context,
            bot: discord.Client,
    ):
        raw = await db_fetch_object(
            guildId=ctx.guild.id,
            key='streamer'

        )

        return cls(
            raw=raw,
            context=ctx,
            bot=bot
        )

    def __init__(
            self,
            context: commands.Context,
            bot: discord.Client,
            raw: dict,
    ):
        self.raw = raw
        self.ctx = context
        self.bot = bot

        if raw and raw['item']['channels']:
            ids = list(raw['item']['channels'])
            members = [context.guild.get_member(int(raw['item']['channels'][i])) for i in ids]
            options = [
                discord.SelectOption(
                    label=str(members[i]),
                    value=ids[i],
                    emoji=Emo.STREAMER
                ) for i in range(len(ids))
            ]
            options.insert(
                0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS)
            )
        else:
            options = [
                discord.SelectOption(
                    label='Please add a streamer first',
                    emoji=Emo.WARN,
                    value='0'
                )
            ]
            options.insert(
                0, discord.SelectOption(label='​', value='0', emoji=Emo.CROSS)
            )

        super().__init__(
            placeholder='Select a streamer',
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
                raw = self.raw
                raw['item']['channels'].pop(self.values[0])
                await db_push_object(
                    guildId=self.ctx.guild.id,
                    key='streamer',
                    item=raw['item']
                )
                await interaction.message.edit(
                    embed=emd,
                    view=None
                )
            elif self.values[0] == '0':
                try:
                    await interaction.message.delete()
                except discord.errors.NotFound:
                    pass


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.message = None
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


async def sub_view_streamer(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    data = await db_fetch_object(
        guildId=ctx.guild.id,
        key='streamer'
    )
    if data and data['item']['role'].isdigit():
        role = ctx.guild.get_role(int(data['item']['role']))
    else:
        role = None

    if role:
        string = f'{role.mention}'
    else:
        try:
            role = await ctx.guild.create_role(
                name='STREAMING NOW',
                mentionable=False,
                hoist=True,
            )
            await db_push_object(
                guildId=ctx.guild.id,
                key='streamer',
                item={'role': str(role.id), 'channels': {}}
            )
            string = f'{role.mention}'
        except discord.errors.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{Emo.WARN} I can\'t create a role in this server.'
                                f'\n\nPlease make sure I have the `Manage Roles` permission.'
                )
            )
            return

    emd = discord.Embed(
        description=f'**{ctx.guild.name}\'s** current **streamer role** is {string}'
                    f'\n\n{Emo.WARN} **Note:**'
                    f'\nYou can customize this role\'s `color` `name` `permissions` etc.'
                    f'\nMake sure the position of the role is lower than my role.'
                    f'\n\nTo set new **Streamer** tap **` Edit `**'
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

    view = Option(ctx)
    await interaction.response.edit_message(embed=emd, view=view)
    await view.wait()

    if view.value == 1:
        new = await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please mention a **Member** to add as **Streamer:**'
            ),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=60)
            mentions = response.mentions
            member = mentions[0] if mentions else None
            try:
                await new.delete()
            except discord.errors.NotFound:
                pass
            if member:
                if not member.bot:
                    prompt = await ctx.send(
                        content=f'{ctx.author.mention}',
                        embed=discord.Embed(
                            description=f'{Emo.CHECK} **{ctx.guild.name}\'s** '
                                        f'new streamer is {member.mention}',
                        )
                    )
                    await prompt.edit(
                        embed=discord.Embed(
                            description='Paste a YouTube Channel **ID** or **URL** for this **Streamer:**'
                        ),
                    )
                    resp = await bot.wait_for('message', check=check, timeout=60)
                    try:
                        channel = Channel(resp.content)
                        info = channel.info
                        emd = discord.Embed(
                            title=f'{Emo.YT} {info["name"]}',
                            description=f'**` Subs `  {info["subscribers"]}**'
                                        f'\n\n**` Views `  {info["views"]}**'
                                        f'\n\n**` Id `  {info["id"]}**',
                            url=info["url"]
                        )
                        if info["avatar_url"] and info["banner_url"]:
                            emd.set_thumbnail(url=info["avatar_url"])
                            emd.set_image(url=info["banner_url"])
                        emd.set_footer(text='✅ Channel has been added successfully.')
                        await prompt.edit(
                            embed=emd,
                        )
                        data['item']['channels'][channel.id] = str(member.id)
                        await db_push_object(
                            guildId=ctx.guild.id,
                            key='streamer',
                            item=data['item']
                        )
                        old_data = await db_fetch_object(
                            guildId=ctx.guild.id,
                            key='youtube'
                        )
                        if old_data:
                            raw = old_data['item']
                            raw[channel.id] = {'live': 'empty', 'upload': channel.latest.id}
                            await db_push_object(
                                guildId=ctx.guild.id,
                                item=raw,
                                key='youtube'
                            )
                        else:
                            init_dict = dict()
                            init_dict[channel.id] = {'live': 'empty', 'upload': channel.latest.id}
                            await db_push_object(
                                guildId=ctx.guild.id,
                                item=empty,
                                key='youtube'
                            )
                    except Exception:
                        traceback.print_exception(*sys.exc_info())
                        await prompt.edit(
                            embed=discord.Embed(
                                description=f'{Emo.WARN} Something went wrong, please try again.'
                                            f'\nProbably the given YouTube Channel ID or URL is invalid.'
                            )
                        )
                        return

            else:
                await ctx.send(
                    content=f'{ctx.author.mention}',
                    embed=discord.Embed(
                        description=f'{Emo.WARN}'
                                    f' you did not mention a member properly.'
                    )
                )
                return
        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')
    elif view.value == 2:
        view = Temp()
        view.add_item(await StreamerList.create(ctx, bot))
        await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please select a Streamer to **remove:**'
            ),
            view=view
        )

    elif view.value == 0:
        await interaction.message.delete()
