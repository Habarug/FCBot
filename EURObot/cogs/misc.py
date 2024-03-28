from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def talk(self, ctx: commands.Context):
        await ctx.channel.send("AMOGUS")

    @commands.command()
    async def echo(self, ctx: commands.Context):
        await ctx.channel.send(ctx.message.content)

async def setup(bot):
    await bot.add_cog(Misc(bot))