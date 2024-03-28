import discord
import os
import pyjson5
from discord.ext import commands


class Bot(commands.Bot):

    def __init__(self, command_prefix="!"):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            status=discord.Status.online,
        )

        self.curDir = os.path.dirname(__file__)

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


def main():
    with open(os.path.join(os.path.dirname(__file__), "config", "PRIVATE.json5")) as f:
        priv = pyjson5.load(f)

    with open(os.path.join(os.path.dirname(__file__), "config", "PUBLIC.json5")) as f:
        pub = pyjson5.load(f)

    bot = Bot(command_prefix=pub["command_prefix"])

    bot.run(priv["token"])


if __name__ == "__main__":
    main()
