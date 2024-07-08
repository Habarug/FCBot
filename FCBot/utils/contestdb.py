import os

import aiosqlite


class ContestDB:
    curDir = os.path.dirname(__file__)
    databaseDir = os.path.join(curDir, "..", "..", "db")
    filepath = os.path.join(databaseDir, "contestdb.db")

    def __init__(self):
        """Instantiate instance of ContestDB class"""
        self.setup_db()

    def setup_db(self):
        if not os.path.exists(self.databaseDir):
            os.mkdir(self.databaseDir)

        with aiosqlite.connect(self.filepath) as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS tournaments(
                name TEXT,
                code TEXT,
                emblem TEXT,
                type TEXT,
                numberOfAvailableSeasons INTEGER)"""
            )
