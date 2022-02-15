from email.policy import default
from django.core.management.base import BaseCommand, CommandError
from codeguru.models import Profile, User, CgGroup
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Load scores to scoreboard from csv file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='File to load scores from')
        parser.add_argument('--score_func', type=str, default='lambda x: x', help='Score function. (variables: sum, max)')

    def handle(self, *args, **options):

        if not options['file'] or not os.path.isfile(options['file']):
            raise CommandError('File does not exist.')
        
        def update_score(team: str, score: int) -> None:
            # assumes name is CNT_GroupName (allows underscores in team name)
            center = team.split("_", 1)[0]
            team_name = team.split("_", 1)[1]

            self.stdout.write(f"Group: {team_name} Score: {score}")
            f_score = func(score)

            # get group
            group = CgGroup.objects.get(name=team_name, center=center)
            members = Profile.objects.filter(group=group)
            for member in members:
                member.score += f_score
                member.save()
                self.stdout.write(self.style.SUCCESS(f"{member.user.username} {member.score} (+{f_score})"))
            

        # load file
        results = pd.read_csv(options['file'])
        # sum scores
        score_sum = int(results.sum(axis = 1, skipna = True).sum())
        socre_max = int(results.max(axis = 1, skipna = True).max())
        try:
            score_func = options['score_func'].format(sum=score_sum, max=socre_max)
            print(score_func)
            func = eval(score_func, globals())
        except Exception as e:
            raise CommandError(f'Invalid score function. {e} (allowed variables are: sum, max)')
        # run update statement for each group
        results.apply(lambda row: update_score(row[0], row[1]), axis=1)

