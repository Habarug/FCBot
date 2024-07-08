import logging
import os

import pyjson5

from .main import FCBot


def replit_run():
    """Function to run the bot on Replit, where tokens and API keys are stored as secrets"""
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PUBLIC.json5")
    ) as f:
        pub = pyjson5.load(f)

    bot = FCBot(
        FD_API_key=os.getenv("FD_API_KEY"),
        competition=pub["competition"],
        season=pub["season"],
        command_prefix=pub["command_prefix"],
    )

    bot.run(
        os.getenv("DISCORD_TOKEN"), log_handler=bot.handler, log_level=logging.DEBUG
    )


if __name__ == "__main__":
    replit_run()
