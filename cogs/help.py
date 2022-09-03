import discord
import neocord


class Help(neocord.cog):

    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.command(name='help', description='information about the features')
    async def help_command(self, ctx: neocord.Context):
        inv = 'https://top.gg/bot/848304171814879273/invite'
        sup = 'https://discord.gg/VE5qRFfmG2'
        uv = 'https://top.gg/bot/848304171814879273/vote'

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Support', style=discord.ButtonStyle.link, url=sup))
        view.add_item(discord.ui.Button(label='Invite', style=discord.ButtonStyle.link, url=inv))
        view.add_item(discord.ui.Button(label='Upvote', style=discord.ButtonStyle.link, url=uv))

        embed = discord.Embed(title='Commands', color=discord.Color.red())
        embed.description = (
            f'\n\n1️⃣ </setup youtube:936634659763286076>'
            f'\n● set up the YouTube channel for the server'
            f'\n\n2️⃣ </setup welcomer:936634659763286076>'
            f'\n● set up the welcome message for the server'
            f'\n\n3️⃣ </setup ping_role:936634659763286076>'
            f'\n● set up the ping role for the server'
            f'\n\n4️⃣ </setup custom_message:936634659763286076>'
            f'\n● set up the custom message for the server'
            f'\n\n5️⃣ </more remove:936634659763286076>'
            f'\n● remove a specific option'
            f'\n\n6️⃣ </more overview:936634659763286076>'
            f'\n● see any current settings'
            f'\n\n7️⃣ </force:936634659763286076>'
            f'\n● force a scan youtube channels for new videos'
        )
        await ctx.send_response(embed=embed, view=view)


async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Help(bot))