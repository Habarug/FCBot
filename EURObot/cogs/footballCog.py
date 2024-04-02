import os
from datetime import datetime as dt

import pandas as pd
from discord.ext import commands, tasks
from discord.utils import format_dt
from footballData import footballData


class FootballCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.competition = self.bot.competition
        self.season = self.bot.season

        self.setup_FD(self.bot.FD_API_key)

        self.update_matches.start()

    def setup_FD(self, FD_API_key):
        print("Setting up Football Data API access")
        self.FD = footballData.FootballData(FD_API_key)

        if not os.path.exists(os.path.join(self.bot.curDir, "files")):
            os.mkdir(os.path.join(self.bot.curDir, "files"))

        if not os.path.exists(
            os.path.join(self.bot.curDir, "files", "competitions.csv")
        ):
            self.competitions_df = self.FD.get_competitions()
            self.competitions_df.to_csv(
                os.path.join(self.bot.curDir, "files", "competitions.csv")
            )
        else:
            self.competitions_df = pd.read_csv(
                os.path.join(self.bot.curDir, "files", "competitions.csv")
            )

        try:
            self.competition_name = self.competitions_df[
                self.competitions_df["code"] == self.competition
            ]["name"]
        except:
            raise ValueError(f"Competition code {self.competition} not recognised")
        else:
            print(
                f"Football data ready. Current competition: {self.competition_name} {self.season}"
            )

    @tasks.loop(minutes=60)  # update matches every X minute
    async def update_matches(self):
        self.matches = self.FD.get_matches(self.competition, self.season)

    @commands.hybrid_command()
    async def upcoming(self, ctx: commands.Context):
        matchday = self.matches[self.matches["utcDate"].dt.date > dt.now().date()]
        msg = "Upcoming matchday: \n"

        for idm, match in matchday[
            matchday["utcDate"].dt.date == matchday["utcDate"].dt.date.iloc[0]
        ].iterrows():
            msg += f"\n{format_dt(match["utcDate"], style = "F")}: {match["homeTeam"]} - {match["awayTeam"]}"

        await ctx.channel.send(msg)


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
