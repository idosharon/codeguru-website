"""
Manual-ish load scores from csv file
Points are for scoreboard, not game run points

File format:
Group,Points
GSA_Group1,10
OST_Group2,3
etc
"""
import sqlite3

from django.core.management import BaseCommand, CommandError
import pandas as pd

from website.settings import DATABASES

TEAMID_QUERY = "SELECT id FROM codeguru_cggroup where name = ? and center = ?"  # find team id from name and center
UPDATE_QUERY = "UPDATE codeguru_profile SET score = score + ? WHERE group = ?"  # update scores for a group
DATABASE_ADDRESSES = DATABASES["default"]


class Command(BaseCommand):
    help = 'Load scores to scoreboard from csv file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        if not options['file']:
            raise CommandError('No file name')

        con = sqlite3.connect(DATABASE_ADDRESSES["NAME"])
        cursor = con.cursor()

        def update_score(team: str, score: int) -> None:
            # assumes name is CNT_GroupName (allows underscores in team name)
            center = team.split("_", 1)[0]
            name = team.split("_", 1)[1]

            team_id: int = int(cursor.execute(TEAMID_QUERY, (name, center)).fetchone()[0])
            cursor.execute(UPDATE_QUERY, (team_id, score))

        # load file
        results = pd.read_csv(options['file'])
        # run update statement for each group
        results.apply(lambda row: update_score(row['Group'], row['Points']), axis=1)

        # commit changes and close
        con.commit()
        con.close()
