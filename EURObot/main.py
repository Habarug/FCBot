import os

import discord
import pandas as pd
import pyjson5
from discord.ext import commands
from footballData import footballData

import logging


class Bot(commands.Bot):

    def __init__(
        self,
        FD_API_key,
        competition,
        season,
        command_prefix="!",
    ):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            status=discord.Status.online,
        )

        self.curDir = os.path.dirname(__file__)

        self.competition = competition
        self.season = season

        self.setup_logger()
        self.setup_FD(FD_API_key)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def setup_hook(self):
        for filename in os.listdir(os.path.join(self.curDir, "cogs")):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[0:-3]}")
                except Exception as e:
                    raise (e)
                else:
                    print(f"{filename} loaded")

    def setup_logger(self):
        if not os.path.exists(os.path.join(self.curDir, "logs")):
            os.mkdir(os.path.join(self.curDir, "logs"))

        self.handler = logging.FileHandler(
            filename=os.path.join(self.curDir, "logs", "discord.log"),
            encoding="utf-8",
            mode="w",
        )

    def setup_FD(self, FD_API_key):
        print("Setting up Football Data API access")
        self.FD = footballData.FootballData(FD_API_key)

        if not os.path.exists(os.path.join(self.curDir, "files")):
            os.mkdir(os.path.join(self.curDir, "files"))

        if not os.path.exists(os.path.join(self.curDir, "files", "competitions.csv")):
            self.competitions_df = self.FD.get_competitions()
            self.competitions_df.to_csv(
                os.path.join(self.curDir, "files", "competitions.csv")
            )
        else:
            self.competitions_df = pd.read_csv(
                os.path.join(self.curDir, "files", "competitions.csv")
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


def main():
    with open(os.path.join(os.path.dirname(__file__), "config", "PRIVATE.json5")) as f:
        priv = pyjson5.load(f)

    with open(os.path.join(os.path.dirname(__file__), "config", "PUBLIC.json5")) as f:
        pub = pyjson5.load(f)

    bot = Bot(
        FD_API_key=priv["footballData"],
        competition=pub["competition"],
        season=pub["season"],
        command_prefix=pub["command_prefix"],
    )

    bot.run(priv["token"], log_handler=bot.handler)


if __name__ == "__main__":
    main()
