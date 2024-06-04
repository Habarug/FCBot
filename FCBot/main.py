import logging
import os
import sys

import discord
import pyjson5
from discord.ext import commands


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

        # Add the path of this file (curDir) to Python path (sys.path)
        # to ensure relative imports work even if it is run as script
        # from a different directory.
        self.workingdir = os.getcwd()
        self.curDir = os.path.dirname(__file__)

        if self.curDir != self.workingdir:
            sys.path.insert(1, self.curDir)

        # Need to set them here so footballCog can retrieve them after being loaded
        # These may be outdated if they are changed by the user later, use variables in footballCog instead
        self._competition = competition
        self._season = season
        self._FD_API_key = FD_API_key

        self.setup_logger()

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


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PRIVATE.json5")
    ) as f:
        priv = pyjson5.load(f)

    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PUBLIC.json5")
    ) as f:
        pub = pyjson5.load(f)

    bot = Bot(
        FD_API_key=priv["footballData"],
        competition=pub["competition"],
        season=pub["season"],
        command_prefix=pub["command_prefix"],
    )

    bot.run(priv["token"], log_handler=bot.handler, log_level=logging.DEBUG)


def replit_run():
    """Function to run the bot on Replit, where tokens and API keys are stored as secrets"""
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PUBLIC.json5")
    ) as f:
        pub = pyjson5.load(f)

    bot = Bot(
        FD_API_key=os.getenv("FD_API_KEY"),
        competition=pub["competition"],
        season=pub["season"],
        command_prefix=pub["command_prefix"],
    )

    bot.run(
        os.getenv("DISCORD_TOKEN"), log_handler=bot.handler, log_level=logging.DEBUG
    )


if __name__ == "__main__":
    main()
