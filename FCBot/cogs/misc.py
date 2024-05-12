from discord import app_commands
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def talk(self, ctx: commands.Context):
        await ctx.csend("AMOGUS")

    @commands.hybrid_command()
    async def echo(self, ctx: commands.Context):
        await ctx.send(ctx.message.content)

    @commands.command()
    @app_commands.default_permissions(administrator=True)
    @commands.is_owner()
    async def sync_slash_commands(self, ctx: commands.Context):
        """Sync slash commands to discord (USE SPARINGLY)"""
        if ctx.author.guild_permissions.administrator is True:
            await self.bot.tree.sync()
            await ctx.send("Command tree synced")
        else:
            await ctx.send("You must be admin to use this command")


async def setup(bot):
    await bot.add_cog(Misc(bot))
