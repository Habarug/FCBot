import os
from datetime import datetime as dt
from datetime import timedelta as timedelta

import pandas as pd
import pyjson5
import requests

# Resources for football-data API https://docs.football-data.org/general/v4/resources.html


class FootballData:

    url_base = "https://api.football-data.org/v4/"
    t_min = 60  # minimum minutes between same API call

    def __init__(self, KEY):
        self.header = {"X-Auth-Token": KEY}

        self.competitions_time = dt.min
        self.EURO_time = dt.min

    def get_competitions(self):
        """Returns all available competitions as a Pandas Dataframe"""
        time = dt.now()
        if ((time - self.competitions_time).total_seconds() / 60) > self.t_min:
            try:
                response = requests.get(
                    self.url_base + "competitions", headers=self.header
                )
            except Exception as e:
                raise e
            else:
                self.competitions_raw = response.json()
                self.competitions_time = time

            cols = ["name", "code", "emblem", "type", "numberOfAvailableSeasons"]
            self.competitions = pd.DataFrame(columns=cols)

            for comp in self.competitions_raw["competitions"]:
                row = []
                for col in cols:
                    row.append(comp[col])

                self.competitions.loc[len(self.competitions.index)] = row

        return self.competitions

    def get_EURO_matches(self, year=2024):
        time = dt.now()

        if ((time - self.EURO_time).total_seconds() / 60) > self.t_min:
            try:
                response = requests.get(
                    self.url_base + "competitions/EC/matches?season=" + str(year),
                    headers=self.header,
                )
            except Exception as e:
                raise e
            else:
                self.data_raw = response.json()
                self.EURO_matches = self.data_raw["matches"]
                self.EURO_time = time

        return self.EURO_matches


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PRIVATE.json5")
    ) as f:
        priv = pyjson5.load(f)

    FD = FootballData(priv["footballData"])

    return FD


if __name__ == "__main__":
    main()
