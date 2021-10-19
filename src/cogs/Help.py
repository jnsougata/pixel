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

        try:

            p = await prefix_fetcher(self.ctx.guild.id)

            emd = discord.Embed(
                description=f'**{self.ctx.guild.me.name} is created for:**'
                            f'\n\n{Emo.YT}  **`YouTube Alerts`**'
                            f'\n\n{Emo.IMG}  **`Welcome Cards`**'
                            f'\n\n**One command for everything:**'
                            f'\n\n{Emo.MOD} **`{p}settings`** or **`{p}setup`** or **`{p}s`** '
                            f'\n\nAll the features are customizable'
                            f'\nand free. Use the **dropdown** menu  '
                            f'\nbelow to get more info about the '
                            f'\n**features**. If you like these features '
                            f'\nplease make sure to leave a feedback.'
                            f'\n For issues you can always join **[here]'
                            f'(https://discord.gg/UzyEYeYZF9)**',
                color=0x005aef
            )
            emd.set_footer(
                text=f'✅ Thanks | Current Prefix [{p}]  (Timed out)',
            )
            self.remove_item(self.children[0])
            await self.message.edit(embed = emd, view = self)

        except AttributeError:
            return




class Dropdown(discord.ui.Select):

    def __init__(self, context: commands.Context):

        self.ctx = context

        options = [
            discord.SelectOption(label='prefix', value='0', emoji=Emo.TAG),
            discord.SelectOption(label='receiver', value='1', emoji=Emo.PING),
            discord.SelectOption(label='youtube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='reception', value='3', emoji=Emo.DEAL),
            discord.SelectOption(label='welcomecard', value='4', emoji=Emo.IMG),
        ]

        super().__init__(
            placeholder = 'Available features',
            min_values = 1,
            max_values = 1,
            options = options
        )


    async def callback(self, interaction: discord.Interaction):

        page_1 = discord.Embed(
            title=f'{Emo.SETTINGS} Prefix',
            description=f'Used to add or remove custom prefix '
                        f'\nto your server. you can change it anytime',
            colour=0x005aef
        )
        page_2 = discord.Embed(
            title=f'{Emo.SETTINGS} Receiver',
            description=f'Used to add or remove the text channel added'
                        f'\nto receive youtube alerts for your server',

            colour=0x005aef
        )
        page_3 = discord.Embed(

            title=f'{Emo.SETTINGS} YouTube',
            description=f'Used to add or remove youtube channel '
                        f'\nto your server to receive live alerts',

            colour=0x005aef
        )
        page_4 = discord.Embed(

            title=f'{Emo.SETTINGS} Reception',
            description=f'Used to add or remove the text channel'
                        f'\nto receive youtube live notifications',

            colour=0x005aef
        )
        page_5 = discord.Embed(

            title=f'{Emo.SETTINGS} Welcome Card',
            description=f'Used to add or remove the welcome card / image'
                        f'\nto your server for welcoming new members',
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
            description = f'**{ctx.guild.me.name} is created for:**'
                          f'\n\n{Emo.YT}  **`YouTube Alerts`**'
                          f'\n\n{Emo.IMG}  **`Welcome Cards`**'
                          f'\n\n**One command for everything:**'
                          f'\n\n{Emo.MOD} **`{p}settings`** or **`{p}setup`** or **`{p}s`** '
                          f'\n\nAll the features are customizable'
                          f'\nand free. Use the **dropdown** menu  '
                          f'\nbelow to get more info about the '
                          f'\n**features**. If you like these features '
                          f'\nplease make sure to leave a feedback.'
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
