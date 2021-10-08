import asyncio
from asynctube import Channel
from src.extras.func import *
from discord.ext import commands
from src.extras.emojis import Emo



class Remove(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.group(name='remove', invoke_without_command=True)
    async def remove(self, ctx):
        prefix = await prefix_fetcher(ctx.guild.id)
        emd = discord.Embed(
            title=f'{Emo.WARN} Subcommand Missing {Emo.WARN}',
            description=f'**You can use following:**'
                        f'\n\n**`youtube`**'
                        f'\n- removes a YouTube channel'
                        f'\n\n**`prefix`**'
                        f'\n- removes custom prefix'
                        f'\n\n**`reception`**'
                        f'\n- removes text channel of welcome cards'
                        f'\n\n**`autorole`**'
                        f'\n- removes automatic role'
                        f'\n\n**`welcomecard`**'
                        f'\n- removes welcome card image'
                        f'\n\n**`receiver`**'
                        f'\n- removes text channel of YouTube Alert',
            color=0xff2b2b
        )
        emd.set_footer(text=f'✅ Syntax: {prefix}set  [subcommand]')
        await ctx.send(embed=emd)


    @remove.command(name='reception')
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_reception(self, ctx):
        await ctx.send(
            f'{Emo.DEL} **Reception channel has been removed!**'
        )
        await db_push_object(
            guildId=ctx.guild.id,
            item = ['removed'],
            key='welcome'
        )


    @remove.command(name='autorole')
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_autorole(self, ctx):
        await ctx.send(
            f'{Emo.DEL} **Automatic role has been removed!**'
        )
        await db_push_object(
            guildId=ctx.guild.id,
            item = ['removed'],
            key = 'autorole'
        )


    @remove.command(name='welcomecard')
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_welcomecard(self, ctx):
        await ctx.send(
            f'{Emo.DEL} **Welcome card has been removed!**'
        )
        await db_push_object(
            guildId=ctx.guild.id,
            item = ['removed'],
            key='cover'
        )


    @remove.command(name='receiver')
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_receiver(self, ctx):
        await ctx.send(
            f'{Emo.DEL} **YouTube Alert channel has been removed!**'
        )
        await db_push_object(
            guildId=ctx.guild.id,
            item = ['removed'],
            key='alertchannel'
        )


    @remove.command(name='prefix')
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_prefix(self, ctx):
        await ctx.send(
            f'{Emo.DEL} **Custom prefix has been removed!**'
        )
        await db_push_object(
            guildId=ctx.guild.id,
            item = ['.'],
            key='prefix'
        )

    @remove.command(aliases=['yt', 'youtube'])
    @commands.has_guild_permissions(administrator=True)
    async def group_rmv_youtube(self, ctx, Id: str = None):

        async def pop_handler(YouTubeId: str):
            try:
                channel = Channel(YouTubeId)
                channelId = await channel.id
                existing = await db_fetch_object(
                    guildId = ctx.guild.id,
                    key = 'youtube'
                )
                local_data = existing['item']
                try:
                    local_data.pop(channelId)
                    await ctx.send(
                        f'{Emo.DEL} **YouTube Channel** **`{await channel.name}`** **has been removed**'
                    )
                    await db_push_object(
                        guildId=ctx.guild.id,
                        item = local_data,
                        key = 'youtube'
                    )
                except KeyError:
                    await ctx.send(
                        f'{Emo.RED_CHECK} **`{await channel.name}`** **isn\'t in YouTube Channel List**'
                    )
            except:
                await ctx.send(
                    f'{Emo.WARN} **Invalid YouTube Channel ID / URL!**'
                )

        if Id is None:

            def check(m):
                return m.author == ctx.author

            await ctx.send(f'**Type YouTube Channel ID / URL to remove:**')

            try:
                reply = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Bye! you took so long!')
                return

            await pop_handler(reply.content)

        else:
            await pop_handler(Id)


def setup(bot):
    bot.add_cog(Remove(bot))