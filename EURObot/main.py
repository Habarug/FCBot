import os

import discord
import footballData
import pandas as pd
import pyjson5
from discord.ext import commands


class Bot(commands.Bot):

    def __init__(self, competition, season, command_prefix="!",):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            status=discord.Status.online,
        )

        self.curDir = os.path.dirname(__file__)

        self.competition    = competition
        self.season         = season

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        print(f"Current competition: ")

    async def setup_hook(self):
        for filename in os.listdir(os.path.join(self.curDir, "cogs")):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[0:-3]}")
                except Exception as e:
                    raise (e)
                else:
                    print(f"{filename} loaded")


def main():
    with open(os.path.join(os.path.dirname(__file__), "config", "PRIVATE.json5")) as f:
        priv = pyjson5.load(f)

    with open(os.path.join(os.path.dirname(__file__), "config", "PUBLIC.json5")) as f:
        pub = pyjson5.load(f)

    bot = Bot(competition = pub["competition"], season = pub["season"], command_prefix=pub["command_prefix"])

    bot.run(priv["token"])


if __name__ == "__main__":
    main()
