import requests
import os
import pyjson5


class FootballData:

    url_base = "https://api.football-data.org/v4/"

    def __init__(self, KEY):
        self.header = {"X-Auth-Token": self.key}


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PRIVATE.json5")
    ) as f:
        priv = pyjson5.load(f)

    FD = FootballData(priv["football_data"])

    return FD
