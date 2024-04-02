import os
from datetime import datetime as dt

import pandas as pd
from discord.ext import commands, tasks
from discord.utils import format_dt
from footballData import footballData
import discord


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

    def get_next_matchday(self):
        matchday = self.matches[
            self.matches["utcDate"].dt.date > dt.now().date()
        ]  # only show upcoming matches
        return matchday[
            matchday["utcDate"].dt.date == matchday["utcDate"].dt.date.iloc[0]
        ]  # only show next day

    def format_match(self, match):
        return f"\n{format_dt(match["utcDate"], style = "F")}: {match["homeTeam"]} - {match["awayTeam"]}"

    @tasks.loop(minutes=60)  # update matches every X minute
    async def update_matches(self):
        self.matches = self.FD.get_matches(self.competition, self.season)

    @commands.hybrid_command()
    async def upcoming(self, ctx: commands.Context):
        matchday = self.get_next_matchday()
        msg = "Upcoming matchday: \n"

        for stage in matchday["stage"]:
            matchday_stage = matchday[matchday["stage"] == stage]
            for group in matchday_stage["group"]:
                msg += f"\n{stage} - {group}:".replace("_", " ")
                for idm, match in matchday_stage[
                    matchday_stage["group"] == group
                ].iterrows():
                    msg += self.format_match(match)

        await ctx.channel.send(msg)

    @commands.hybrid_command()
    async def predict_upcoming(self, ctx: commands.Context):
        self.predict_match(self.matches.iloc[0])

    async def predict_match(self, match):
        pass

    class PredictMatch(discord.ui.View):

        def __init__(self):

            self.add_item(discord.ui.TextInput())


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
