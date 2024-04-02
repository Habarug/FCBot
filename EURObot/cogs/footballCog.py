from datetime import datetime as dt

from discord.ext import commands, tasks


class FootballCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.update_matches.start()

    @tasks.loop(minutes=60)  # update matches every X minute
    async def update_matches(self):
        self.matches = self.bot.FD.get_matches(self.bot.competition, self.bot.season)
        self.bot.handler.info("Update matches")

    @commands.command()
    async def upcoming(self, ctx: commands.Context):
        matchday = self.matches[self.matches["date"] > dt.now().date()]
        msg = f"Upcoming matches {matchday["date"].iloc[0].strftime("%d %B %Y")}: \n"

        for idm, match in matchday[matchday["date"] == matchday["date"].iloc[0]].iterrows():
            msg += f"\n{match["time"]}: {match["homeTeam"]} - {match["awayTeam"]}"
        
        await ctx.channel.send(msg)        

async def setup(bot):
    await bot.add_cog(FootballCog(bot))
