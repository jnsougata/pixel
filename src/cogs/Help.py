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

        raw = await db_fetch_object(guildId=ctx.guild.id, key='prefix')

        if raw is not None and len(raw) > 0:
            prefix = raw['item'][0]
        else:
            prefix = '.'


        emd = discord.Embed(color=0x005aef)
        emd.set_author(name=f'Hi {ctx.author.display_name}', url=sup_url, icon_url=ctx.author.avatar_url)
        emd.add_field(name='\u200b', value=f'{Emo.ESB} **[Basic]({basic_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.SETTINGS} **[Special]({spc_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.DATABASE} **[Logging]({log_url})**', inline=False)
        emd.add_field(name='\u200b', value=f'{Emo.MOD} **[Moderation]({mod_url})**\n\u200b', inline=False)
        emd.set_footer(
            text=f' Thanks | Current Prefix( {prefix} )',
            icon_url=ctx.guild.me.avatar_url
        )

        msg = await ctx.send(embed=emd)
        await msg.add_reaction('◀')
        await msg.add_reaction('▶')

        def check(rctn, user):
            return rctn.message.id == msg.id and user == ctx.author


        basic_embed = discord.Embed(title=f'{Emo.BASIC} **Basic Commands**', color=0x005aef)
        basic_embed.add_field(name='av', value='```\nShows your or tagged user\'s large avatar```', inline=False)
        basic_embed.add_field(name='vc', value='```\nMentions tagged Member\'s current VC```', inline=False)
        basic_embed.add_field(name='afk', value='```\nAdds [AFK] with your display name```', inline=False)
        basic_embed.add_field(name='gif', value='```\nGets a GIF from Tenor```', inline=False)
        basic_embed.add_field(name='info', value='```\nShows your or tagged User\'s information```', inline=False)
        basic_embed.add_field(name='roles', value='```\nShows tagged Member\'s roles```', inline=False)
        basic_embed.add_field(name='invite', value='```\nSends a link to add PixeL to other servers```', inline=False)
        basic_embed.add_field(name='ticket', value='```\nHelps to contact Admins or Mods without sending DM```',
                              inline=False)
        basic_embed.add_field(name='server', value='```\nShows brief info of the current server```', inline=False)
        basic_embed.set_footer(text=f'Page: 1 | For more information use {prefix}help [command] ')

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
        special_embed.add_field(
            name='autorole', value='```\nSets a automatic role for your server```',
            inline=False
        )
        special_embed.set_footer(text=f'Page: 2 | For more information use {prefix}help [command]')

        mod_embed = discord.Embed(title=f'{Emo.MOD} Moderation Commands', color=0x005aef)
        mod_embed.add_field(
            name='clear', value='```\nDeletes specified number of messages```',
            inline=False
        )
        mod_embed.add_field(
            name='lock', value='```\nLocks current or mentioned channel```',
            inline=False
        )
        mod_embed.add_field(
            name='unlock', value='```\nUnlocks current or mentioned channel```',
            inline=False
        )
        mod_embed.add_field(
            name='loot', value='```\nAdds custom Emoji to current server```',
            inline=False
        )
        mod_embed.add_field(
            name='poll', value='```\nCreates a poll to desired Text Channel```',
            inline=False
        )
        mod_embed.add_field(
            name='drole', value='```\nRemoves mentioned role from all members```',
            inline=False
        )
        mod_embed.add_field(
            name='embed', value='```\nCreates an Embed to current Text Channel```',
            inline=False
        )
        mod_embed.set_footer(text=f'Page: 3 | For more information use {prefix}help [command]')

        logging_embed = discord.Embed(
            title=f'{Emo.LOGGING} Logging Command',
            description='\n\n**Command:**'
                        '\n\n**` log `**'
                        '```\nCreates a text channel'
                        '\nEnables activity Logging```',
            color=0x005aef
        )
        logging_embed.add_field(
            name='Syntax:',
            value='```\n\nenable [command]```'
                  '```\n\ndisable [command]```',
            inline=False
        )
        logging_embed.set_image(url='https://c.tenor.com/2AQR9FgLS4UAAAAC/do-it-shia-la-beouf.gif')
        logging_embed.set_footer(text=f'Page: 4 | For more information use {prefix}help [command]')


        secret_embed = discord.Embed(
            title=f'{Emo.LOCKED} {ctx.guild.me.display_name}\'s Secret',
            description=f'**` {prefix}naughty `**'
                        f'```\n\nAt last you are here!'
                        f'\nLet me tell you'
                        f'\nmy little secret'
                        f'\nIf you are feeling'
                        f'\nnaughty sometimes'
                        f'\nUse {prefix}naughty'
                        f'\nin any NSFW channel'
                        f'\nSee the black magic'
                        f'\nfeel it and enjoy rest```',
            color=0x005aef
        )
        secret_embed.set_image(url='https://c.tenor.com/spYJzEXz8BsAAAAC/smirk-ryan-reynolds.gif')
        secret_embed.set_footer(text=f'Page: 5 | Just try {prefix}naughty and see')

        embeds = [emd, basic_embed, special_embed, mod_embed, logging_embed, secret_embed]

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
    @help.command(name='av')
    async def help_avatar(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='av',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}av```'
                  f'```\n{prefix}av @user```'
                  f'```\n{prefix}av userid / username```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='vc')
    async def help_get_voice(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='vc',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}vc @user```'
                  f'```\n{prefix}vc userid / username```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='afk')
    async def help_user_afk(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='afk',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}afk```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='gif')
    async def help_gif(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='gif',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}gif <keywords>```'
                  f'```\n{prefix}giphy <keywords>```'
                  f'```\n{prefix}search <keywords>```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='info')
    async def help_user_info(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='info',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}info @user\\id```'
                  f'```\n{prefix}userinfo @user\\id```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='roles')
    async def help_all_roles(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='roles',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}ar @member\\id```'
                  f'```\n{prefix}roles @member\\id```'
                  f'```\n{prefix}allrole @member\\id```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='invite')
    async def help_invite(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='invite',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}invite```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='ticket')
    async def help_ticket(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='ticket',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}mail```'
                  f'```\n{prefix}ticket```'
                  f'```\n{prefix}modmail```',
            inline=False
        )
        await ctx.send(embed=emd)

    @help.command(name='server')
    async def help_guild_info(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='roles',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}guild```'
                  f'```\n{prefix}sinfo```'
                  f'```\n{prefix}server```'
                  f'```\n{prefix}serverinfo```',
            inline=False
        )
        await ctx.send(embed=emd)

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

    @help.command(name='autorole')
    async def help_set_autorole(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='autorole',
            color=0x005aef
        )
        emd.add_field(
            name='Syntax:',
            value=f'```\n{prefix}set autorole```'
                  f'```\n{prefix}remove autorole```',
            inline=False
        )
        await ctx.send(embed=emd)

    # ---> Enable / Disable [Group]

    @commands.group(name='enable', invoke_without_command=True)
    async def enable(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='Subcommand Missing',
            description=f'**Use** **` {prefix}enable log `**'
        )
        await ctx.send(embed=emd)

    @commands.group(name='disable', invoke_without_command=True)
    async def disable(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title='Subcommand Missing',
            description=f'Use** **` {prefix}disable log `**'
        )
        await ctx.send(embed=emd)


def setup(bot):
    bot.add_cog(Help(bot))
