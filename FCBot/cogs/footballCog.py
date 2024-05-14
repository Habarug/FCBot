import os
from datetime import datetime as dt

import discord
import pandas as pd
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import format_dt
from footballData import footballData


class FootballCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.competition = self.bot._competition
        self.season = self.bot._season

        self.setup_FD(self.bot._FD_API_key)

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
        self.matchdays = self.matches["utcDate"].dt.date.unique()

    @commands.hybrid_command(description="Change the current competition")
    @app_commands.default_permissions(administrator=True)
    async def changecompetition(self, ctx: commands.Context):
        """Change the current competition"""

        view = ChangeCompetition(
            self.competitions_df["name"], self.competitions_df["code"]
        )

        await ctx.send("Select new competition", view=view)
        timed_out = await view.wait()

        if timed_out:
            await ctx.send("You did not select a competition, aborted.")
            return

        self.competition = view.code
        self.season = self.FD.get_current_season(self.competition)

        self.update_matches.restart()

        await ctx.send(
            f"Competition successfully changed to: {self.competition} {self.season}"
        )

    #########################
    ### Display matchdays ###
    #########################

    def get_index_of_next_matchday(self):
        return [
            idm
            for idm, matchday in enumerate(self.matchdays)
            if matchday >= dt.now().date()
        ][0]

    def get_matchday(self, idx: int = 0):
        """Get match day

        Args:
            idx : Index of matchday.
        """
        return self.matches[self.matches["utcDate"].dt.date == self.matchdays[idx]]

    async def display_matchday(self, ctx: commands.Context, matchday_idx):
        """Displays a given matchday given by the index and buttons to show previous or next"""
        matchday = self.get_matchday(idx=matchday_idx)

        view = UpcomingMatchesButtons(
            show_next=matchday_idx < len(self.matchdays), show_prev=matchday_idx > 0
        )

        await ctx.send(format_matchday(matchday), view=view)
        await view.wait()

        if view.values[0]:
            await self.display_matchday(ctx, matchday_idx - 1)
        elif view.values[1]:
            await self.display_matchday(ctx, matchday_idx + 1)

    @commands.hybrid_command()
    async def upcoming(self, ctx: commands.Context):
        """Show upcoming match day"""
        matchday_idx = self.get_index_of_next_matchday()

        await self.display_matchday(ctx, matchday_idx)

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

        await ctx.send(format_match(match, predict=view.goals), ephemeral=True)


####################################
### Upcoming matches UI elements ###
####################################


class CustomButton(discord.ui.Button):
    def __init__(self, idx, **kwargs):
        super().__init__(**kwargs)
        self.idx = idx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.values[self.idx] = 1
        self.view.stop()


class UpcomingMatchesButtons(discord.ui.View):
    def __init__(self, show_prev=True, show_next=True):
        super().__init__()

        self.values = [0, 0]  # 1 for pressed buttons

        self.add_item(
            CustomButton(idx=0, label="Previous matchday", disabled=not show_prev)
        )
        self.add_item(
            CustomButton(idx=1, label="Next matchday", disabled=not show_next)
        )


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


######################################
### Change competition UI elements ###
######################################


class CompetitionDropdown(discord.ui.Select):
    def __init__(self, names: pd.Series, codes: pd.Series):
        options = [
            (discord.SelectOption(label=name, value=code))
            for name, code in zip(names, codes)
        ]

        super().__init__(
            placeholder="Select new competition",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.code = self.values[0]
        self.view.stop()
        return


class ChangeCompetition(discord.ui.View):
    def __init__(self, names: pd.Series, codes: pd.Series):
        super().__init__(timeout=60)
        self.code = ""
        self.add_item(CompetitionDropdown(names=names, codes=codes))


#########################
### Utility functions ###
#########################


def format_match(match, predict: dict = None):
    if (
        match["status"] == "FINISHED"
    ):  # Display goals for finished or ongoing games. Bold if finished
        homeGoals = f"**{match["homeGoals"]}**"
        awayGoals = f"**{match["awayGoals"]}**"
    elif match["status"] == "IN_PLAY":
        homeGoals = match["homeGoals"]
        awayGoals = match["awayGoals"]
    else:  # If not finished or ongoing, don't print score
        homeGoals = ""
        awayGoals = ""

    string = f"\n{format_dt(match["utcDate"], style = "t")}: {match["homeTeam"]} {homeGoals}-{awayGoals} {match["awayTeam"]}"
    if predict:
        string += (
            f". Prediction: {predict[match["homeTeam"]]}-{predict[match["awayTeam"]]}"
        )

    return string


def format_matchday(matchday):
    msg = f"Matchday: {format_dt(matchday["utcDate"].iloc[0], style = "D")}\n"

    for stage in matchday["stage"].unique():
        matchday_stage = matchday[matchday["stage"] == stage]
        for group in matchday_stage["group"].unique():
            if group is not None:
                msg += f"\n{stage} - {group}:".replace("_", " ")
                for idm, match in matchday_stage[
                    matchday_stage["group"] == group
                ].iterrows():
                    msg += format_match(match)
            else:
                msg += f"\n{stage}:".replace("_", " ")
                for idm, match in matchday_stage.iterrows():
                    msg += format_match(match)

    return msg


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
