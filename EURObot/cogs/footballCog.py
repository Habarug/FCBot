from discord.ext import tasks, commands
from datetime import datetime as dt


class FootballCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.update_matches.start()

    @tasks.loop(minutes=60)  # update matches every X minute
    async def update_matches(self):
        self.matches = self.bot.FD.get_matches(self.bot.competition, self.bot.season)
        print("Matches updated")


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
