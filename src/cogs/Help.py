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
        self.timeout = 60
        self.add_item(Dropdown(ctx))
        self.add_item(INVITE)
        self.add_item(VOTE)


    async def on_timeout(self) -> None:

        try:
            await self.message.delete()
        except:
            return


class Dropdown(discord.ui.Select):

    def __init__(self, context: commands.Context):

        self.ctx = context

        options = [
            discord.SelectOption(label='​', value='x', emoji=Emo.BACK),
            discord.SelectOption(label='prefix', value='0', emoji=Emo.TAG),
            discord.SelectOption(label='receiver', value='1', emoji=Emo.PING),
            discord.SelectOption(label='youtube', value='2', emoji=Emo.YT),
            discord.SelectOption(label='reception', value='3', emoji=Emo.DEAL),
            discord.SelectOption(label='welcomecard', value='4', emoji=Emo.IMG),
        ]

        super().__init__(
            placeholder = 'About setup options',
            min_values = 1,
            max_values = 1,
            options = options
        )


    async def callback(self, interaction: discord.Interaction):


        page_1 = discord.Embed(
            title=f'{Emo.TAG} Prefix',
            description=f'Used to add or remove custom prefix '
                        f'\nto your server. you can change it anytime',
            colour=0x005aef
        )
        page_2 = discord.Embed(
            title=f'{Emo.PING} Receiver',
            description=f'Used to add or remove the text channel'
                        f'\nadded to receive youtube alerts for your server',

            colour=0x005aef
        )
        page_3 = discord.Embed(

            title=f'{Emo.YT} YouTube',
            description=f'Used to add or remove youtube'
                        f'\nchannel to your server to receive live alerts',

            colour=0x005aef
        )
        page_4 = discord.Embed(

            title=f'{Emo.DEAL} Reception',
            description=f'Used to add or remove the text'
                        f'\nchannel for receiving welcome message cards',

            colour=0x005aef
        )
        page_5 = discord.Embed(

            title=f'{Emo.IMG} Welcome Card',
            description=f'Used to add or remove the welcome card or'
                        f'\nimage to your server for welcoming new members',
            colour=0x005aef
        )

        book = [page_1, page_2, page_3, page_4, page_5]


        if interaction.user == self.ctx.author:

            if self.values[0].isdigit():
                await interaction.message.edit(embed=book[int(self.values[0])])
            else:
                raw = await db_fetch_object(
                    guildId=self.ctx.guild.id,
                    key='prefix'
                )

                if raw and len(raw) > 0:
                    p = raw['item'][0]
                else:
                    p = '.'

                emd = discord.Embed(
                    description=f''
                                f'\n\n{Emo.SETTINGS} To set me up'
                                f'\n use command **{p}setup**'
                                f'\n\n{Emo.FAQ} To know about **setup**'
                                f'\noptions use the **dropdown** menu'
                                f'\n\n{Emo.SUP} For issues join **[PixeL Support]'
                                f'(https://discord.gg/UzyEYeYZF9)**'
                                f'\n​‍‍‍',
                    color=0x005aef
                )
                emd.set_author(
                    name=self.ctx.author,
                    icon_url=self.ctx.author.avatar.url
                )
                emd.set_footer(
                    text=f'✅ Thanks | Current Prefix [{p}]',
                )

                await interaction.message.edit(embed=emd)

        else:

            await interaction.response.send_message(
                'You are not allowed to control this message!', ephemeral=True
            )



class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='help')
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
            description=f''
                        f'\n\n{Emo.SETTINGS} To set me up'
                        f'\n use command **{p}setup**'
                        f'\n\n{Emo.FAQ} To know about **setup**'
                        f'\noptions use the **dropdown** menu'
                        f'\n\n{Emo.SUP} For issues join **[PixeL Support]'
                        f'(https://discord.gg/UzyEYeYZF9)**'
                        f'\n​‍‍‍',
            color=0x005aef
        )
        emd.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar.url
        )
        emd.set_footer(
            text=f'✅ Thanks | Current Prefix [{p}]',
        )

        view = CustomView(ctx)
        view.message = await ctx.send(embed=emd, view = view)


def setup(bot):
    bot.add_cog(Help(bot))
