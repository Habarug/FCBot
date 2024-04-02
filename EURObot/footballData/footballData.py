import os
from datetime import datetime as dt
from datetime import timedelta as timedelta

import pandas as pd
import pyjson5
import requests

# Resources for football-data API https://docs.football-data.org/general/v4/resources.html


class FootballData:

    url_base = "https://api.football-data.org/v4/"
    t_min = 15  # minimum minutes between same API call

    def __init__(self, KEY):
        self.header = {"X-Auth-Token": KEY}

        self.competitions_time = dt.min
        self.matches = dict()
        self.matches_time = dict()

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

    def get_matches(self, competition, season):
        cols = [
            "homeTeam",
            "awayTeam",
            "winner",
            "homeGoals",
            "awayGoals",
            "status",
            "utcDate",
            "stage",
            "group",
        ]

        if competition not in self.matches:
            self.matches_time[competition] = dt.min

        time = dt.now()

        if ((time - self.matches_time[competition]).total_seconds() / 60) > self.t_min:
            try:
                response = requests.get(
                    self.url_base
                    + f"competitions/{competition}/matches?season={str(season)}",
                    headers=self.header,
                )
            except Exception as e:
                raise e
            else:
                data_raw = response.json()
                matches_raw = data_raw["matches"]

            self.matches[competition] = pd.DataFrame(columns=cols)

            for match in matches_raw:
                row = []
                for col in cols:
                    if col == "winner":
                        val = match["score"]["winner"]
                    elif col == "homeGoals":
                        val = match["score"]["fullTime"]["home"]
                    elif col == "awayGoals":
                        val = match["score"]["fullTime"]["away"]
                    else:
                        val = match[col]

                        if isinstance(val, dict):
                            val = val["name"]

                    row.append(val)

                self.matches[competition].loc[
                    len(self.matches[competition].index)
                ] = row

            self.matches[competition]["utcDate"] = pd.to_datetime(
                self.matches[competition]["utcDate"]
            )

            self.matches_time[competition] = dt.now()

        return self.matches[competition]


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "..", "config", "PRIVATE.json5")
    ) as f:
        priv = pyjson5.load(f)

    FD = FootballData(priv["footballData"])

    return FD


if __name__ == "__main__":
    main()
