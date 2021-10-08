import asyncio
from src.extras.func import *
from discord.ext import commands
from src.extras.emojis import Emo


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='help', invoke_without_command=True)
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.member)
    async def help(self, ctx):

        sup_url = 'https://top.gg/servers/834662394068336670/join/'
        basic_url = 'https://verified.gitbook.io/pixel-docs/basic-commands/afk'
        mod_url = 'https://verified.gitbook.io/pixel-docs/moderation/clear'
        spc_url = 'https://verified.gitbook.io/pixel-docs/special/welcome'
        log_url = 'https://verified.gitbook.io/pixel-docs/activity-logging/enable'

        raw = await db_fetch_object(
            guildId=ctx.guild.id, 
            key='prefix'
            )


        if raw and len(raw) > 0:
            prefix = raw['item'][0]
        else:
            prefix = '-'


        emd = discord.Embed(color=0x005aef)
        emd.set_author(name=f'Hi {ctx.author.display_name}', url=sup_url, icon_url=ctx.author.avatar_url)
        emd.add_field(name='\u200b', value=f'{Emo.ESB} **[Basic]({basic_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.SETTINGS} **[Special]({spc_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.DATABASE} **[Logging]({log_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.MOD} **[Moderation]({mod_url})**\n\u200b', inline=False)
        emd.set_footer(
            text=f' Thanks | Current Prefix ( {prefix} )',
            icon_url=ctx.guild.me.avatar_url
        )

        msg = await ctx.send(embed=emd)
        await msg.add_reaction('◀')
        await msg.add_reaction('▶')


        def check(reactz, user):
            return reactz.message.id == msg.id and user == ctx.author


        
        special_embed = discord.Embed(
            title=f'{Emo.SPECIAL} Special Commands',
            description='**Syntax:** set [command] | remove [command]\n\n**Commands:**',
            color=0x005aef
        )
        special_embed.add_field(
            name='prefix', value='```\nSets a custom prefix for your server```',
            inline=False
        )
        special_embed.add_field(
            name='reception', value='```\nSets a text channel for welcome cards```',
            inline=False
        )
        special_embed.add_field(
            name='youtube', value='```\nSets YouTube channel for Live / Upload alerts```',
            inline=False
        )
        special_embed.add_field(
            name='welcomecard', value='```\nSets custom welcome card / image```',
            inline=False
        )
        special_embed.add_field(
            name='receiver', value='```\nSets a text channel to receive YouTube Alerts```',
            inline=False
        )
        special_embed.set_footer(text=f'Page: 2 | For more information use {prefix}help [command]')

        
        embeds = [emd, special_embed]


        page = 0
        while True:
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=180, check=check)
                if reaction.emoji == '▶' and page < len(embeds) - 1:
                    page += 1
                    await msg.remove_reaction('▶', ctx.author)
                    await msg.edit(embed=embeds[page])


                elif reaction.emoji == '◀' and page == 0:
                    await msg.remove_reaction('◀', ctx.author)
                    await msg.edit(embed=embeds[0])



                elif reaction.emoji == '▶' and page == len(embeds) - 1:
                    page = 0
                    await msg.remove_reaction('▶', ctx.author)
                    await msg.edit(embed=embeds[0])


                elif reaction.emoji == '◀' and page >= 1:
                    page -= 1
                    await msg.remove_reaction('◀', ctx.author)
                    await msg.edit(embed=embeds[page])


            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return


    # ---> Groups


    @help.command(name='prefix')
    async def help_prefix(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='prefix',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set prefix```'
                  f'```\n{prefix}remove prefix```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='reception')
    async def help_set_reception(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='welcome',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set reception```'
                  f'```\n{prefix}remove reception```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='youtube')
    async def help_set_youtube(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='youtube',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set youtube```'
                  f'```\n{prefix}remove youtube```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='welcomecard')
    async def help_set_welcomecard(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='coverpic',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set welcomecard```'
                  f'```\n{prefix}remove welcomecard```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='receiver')
    async def help_set_receiver(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='recipient',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set receiver```'
                  f'```\n{prefix}remove receiver```',
            inline=False
        )
        await ctx.send(embed=emd)


def setup(bot):
    bot.add_cog(Help(bot))
