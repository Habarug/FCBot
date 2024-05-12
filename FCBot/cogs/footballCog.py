import os
from datetime import datetime as dt

import discord
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
        except Exception:
            raise ValueError(f"Competition code {self.competition} not recognised")
        else:
            print(
                f"Football data ready. Current competition: {self.competition_name} {self.season}"
            )

    @tasks.loop(minutes=60)  # update matches every X minute
    async def update_matches(self):
        """Loop to update matches"""
        self.matches = self.FD.get_matches(self.competition, self.season)

    def get_matchday(self, idx: int = 0):
        """Get match day

        Args:
            idx : Index of matchday. Default = 0 : Next matchday
        """
        matchday = self.matches[
            self.matches["utcDate"].dt.date > dt.now().date()
        ]  # only show upcoming matches
        return matchday[
            matchday["utcDate"].dt.date == matchday["utcDate"].dt.date.iloc[idx]
        ]  # only show specified matchday

    @commands.hybrid_command()
    async def upcoming(self, ctx: commands.Context):
        """Show upcoming match day"""
        matchday = self.get_matchday(idx=0)
        msg = "Upcoming matchday: \n"

        for stage in matchday["stage"]:
            matchday_stage = matchday[matchday["stage"] == stage]
            for group in matchday_stage["group"]:
                msg += f"\n{stage} - {group}:".replace("_", " ")
                for idm, match in matchday_stage[
                    matchday_stage["group"] == group
                ].iterrows():
                    msg += format_match(match)

        await ctx.send(msg)

    ########################
    ### Match prediction ###
    ########################

    @commands.hybrid_command()
    async def predict(self, ctx: commands.Context):
        await self.predict_match(ctx, self.matches.iloc[0])  # Placeholder lol

    async def predict_match(self, ctx: commands.Context, match: pd.Series):
        homeTeam = match["homeTeam"]
        awayTeam = match["awayTeam"]
        view = PredictMatch(homeTeam, awayTeam)
        await ctx.send(
            f"Enter your prediction for {homeTeam}-{awayTeam}",
            view=view,
            ephemeral=True,
        )
        timed_out = await view.wait()

        if timed_out:
            await ctx.send("You did not enter a prediction", ephemeral=True)
            return

        await ctx.send(format_match_score(match, view.goals), ephemeral=True)


####################################
### Match prediction UI elements ###
####################################


class GoalDropdown(discord.ui.Select):
    def __init__(self, team: str):
        self.team = team
        options = [(discord.SelectOption(label=str(i))) for i in range(10)]

        super().__init__(
            placeholder=f"Goals for {team}:",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.goals[self.team] = self.values[0]

        if len(self.view.goals) > 1:
            self.view.stop()
            return


class PredictMatch(discord.ui.View):
    def __init__(self, homeTeam: str, awayTeam: str):
        super().__init__(timeout=60)
        self.goals = {}
        self.add_item(GoalDropdown(homeTeam))
        self.add_item(GoalDropdown(awayTeam))


#########################
### Utility functions ###
#########################


def format_match(match):
    return f"\n{format_dt(match["utcDate"], style = "F")}: {match["homeTeam"]} - {match["awayTeam"]}"


def format_match_score(match: pd.Series, goals: dict):
    return f"{match["homeTeam"]} {goals[match["homeTeam"]]}-{goals[match["awayTeam"]]} {match["awayTeam"]}"


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
