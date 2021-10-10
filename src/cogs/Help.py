import discord
from src.extras.func import *
from discord.ext import commands
from src.extras.emojis import Emo



class CustomView(discord.ui.View):

    def __init__(
            self,
            ctx: commands.Context,
            message: discord.Message = None
    ):

        self.ctx = ctx
        self.message = message

        INVITE = discord.ui.Button(
            label='Invite',
            style=discord.ButtonStyle.link,
            url='https://top.gg/bot/848304171814879273/invite'
        )
        VOTE = discord.ui.Button(
            label='Vote here',
            style=discord.ButtonStyle.link,
            url='https://top.gg/bot/848304171814879273/vote'
        )

        super().__init__()
        self.value = None
        self.timeout = 20
        self.add_item(Dropdown(ctx))
        self.add_item(INVITE)
        self.add_item(VOTE)


    async def on_timeout(self) -> None:

        p = await prefix_fetcher(self.ctx.guild.id)

        emd = discord.Embed(
            description=f'**{self.ctx.guild.me.display_name}** is created for:'
                        f'\n\n{Emo.YT}  **`YouTube Alerts`**'
                        f'\n\n{Emo.IMG}  **`Welcome Cards`**'
                        f'\n\n**One command for all:**'
                        f'\n\n{Emo.MOD} **`{p}settings`**'
                        f'\n\nAll the features are customizable'
                        f'\nand free. Use the **dropdown** menu  '
                        f'\nbelow to get more info about the '
                        f'\ncommands. If you like these features '
                        f'\nmake sure to leave a feedback please.'
                        f'\n For issues you can always join **[here]'
                        f'(https://discord.gg/UzyEYeYZF9)**',
            color=0x005aef
        )
        emd.set_footer(
            text=f'✅ Thanks | Current Prefix [{p}]  (*Timed out)',
        )
        self.remove_item(self.children[0])
        await self.message.edit(embed = emd, view = self)




class Dropdown(discord.ui.Select):

    def __init__(self, context: commands.Context):

        self.ctx = context

        options = [
            discord.SelectOption(label='prefix',value='0'),
            discord.SelectOption(label='receiver', value='1'),
            discord.SelectOption(label='youtube', value='2'),
            discord.SelectOption(label='reception', value='3'),
            discord.SelectOption(label='welcomecard', value='4'),
        ]

        super().__init__(
            placeholder = 'Select a command',
            min_values = 1,
            max_values = 1,
            options = options
        )


    async def callback(self, interaction: discord.Interaction):

        p = await prefix_fetcher(id = interaction.guild.id)

        page_1 = discord.Embed(
            title=f'{Emo.SETTINGS} Prefix',
            description=f'shows custom prefix added to'
                        f'\nyour server. you can change it anytime'
                        f'\n\n**` Syntax `**'
                        f'\n```\n{p}prefix```',

            colour=0x005aef
        )
        page_2 = discord.Embed(
            title=f'{Emo.SETTINGS} Receiver',
            description=f'shows the added text channel'
                        f'\nof your server to receive youtube alerts'
                        f'\n\n**` Syntax `**'
                        f'\n```\n{p}receiver```',

            colour=0x005aef
        )
        page_3 = discord.Embed(

            title=f'{Emo.SETTINGS} YouTube',
            description=f'shows the list of youtube channel '
                        f'\nadded to your server to receive alerts'
                        f'\n\n**` Syntax `**'
                        f'\n```\n{p}youtube```',

            colour=0x005aef
        )
        page_4 = discord.Embed(

            title=f'{Emo.SETTINGS} Reception',
            description=f'shows the text channel added'
                        f'\nto receive youtube notifications'
                        f'\n\n**` Syntax `**'
                        f'\n```\n{p}reception```',

            colour=0x005aef
        )
        page_5 = discord.Embed(

            title=f'{Emo.SETTINGS} Welcome Card',
            description=f'shows the welcome card / image'
                        f'\nadded for your server to be used'
                        f'\nto welcome them when a member joins'
                        f'\n\n**` Syntax `**'
                        f'\n```\n{p}welcomecard```',

            colour=0x005aef
        )

        book = [page_1, page_2, page_3, page_4, page_5]


        if interaction.user == self.ctx.author:

            await interaction.message.edit(embed=book[int(self.values[0])])

        else:

            await interaction.response.send_message(
                'You are not allowed to control this message!', ephemeral=True
            )



class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='help', invoke_without_command=True)
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.member)
    async def help(self, ctx):


        raw = await db_fetch_object(
            guildId = ctx.guild.id,
            key = 'prefix'
            )


        if raw and len(raw) > 0:
            p = raw['item'][0]
        else:
            p = '.'


        emd = discord.Embed(
            description = f'**{ctx.guild.me.display_name}** is created for:'
                          f'\n\n{Emo.YT}  **`YouTube Alerts`**'
                          f'\n\n{Emo.IMG}  **`Welcome Cards`**'
                          f'\n\n**One command for all:**'
                          f'\n\n{Emo.MOD} **`{p}settings`**'
                          f'\n\nAll the features are customizable'
                          f'\nand free. Use the **dropdown** menu  '
                          f'\nbelow to get more info about the '
                          f'\ncommands. If you like these features '
                          f'\nmake sure to leave a feedback please.'
                          f'\n For issues you can always join **[here]'
                          f'(https://discord.gg/UzyEYeYZF9)**',
            color=0x005aef
        )
        emd.set_footer(
            text=f'✅ Thanks | Current Prefix [{p}]',
        )

        view = CustomView(ctx)
        view.message = await ctx.send(embed=emd, view = view)


def setup(bot):
    bot.add_cog(Help(bot))
