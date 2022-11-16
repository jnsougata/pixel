import discord
import neocord


class Owner(neocord.cog):

    def __init__(self, bot: neocord.Bot):
        self.bot = bot

    @neocord.cog.default_permission(discord.Permissions.administrator)
    @neocord.cog.command(
        name='remove', 
        description='removes a command',
        dm_access=False,
        options=[
            neocord.IntOption(name="cmd_id" , description="id of the command to remove", required=True),
            neocord.IntOption(name="guild_id" , description="id of the guild to remove the command from", required=False)
        ],
        guild_id=834662394068336670
    )
    async def remove_command(self, ctx: neocord.Context, cmd_id: int, guild_id: int = None):
        if ctx.author.id != 516649677001719819:
            return await ctx.send_message("You are not allowed to use this command...")
        command = await self.bot.fetch_command(cmd_id, guild_id)
        if command is None:
            await ctx.send_message("Command not found...")
            return
        await command.delete()
        await ctx.send_message("Command removed successfully...")
    
    @neocord.cog.default_permission(discord.Permissions.administrator)
    @neocord.cog.command(
        name='ls', 
        description='lists all commands',
        dm_access=False,
        guild_id=834662394068336670
    )
    async def ls_command(self, ctx: neocord.Context, cmd_id: int, guild_id: int = None):
        commands = self.bot.application_commands
        descriptions = "\n".join([f'{command.name} - {command.id} - {command.guild_id}' for command in commands])
        await ctx.send_message(discord.Embed(description=f'```{descriptions}```'))
        

async def setup(bot: neocord.Bot):
    await bot.add_application_cog(Owner(bot))
