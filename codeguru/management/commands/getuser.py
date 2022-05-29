from django.core.management.base import BaseCommand, CommandError
from codeguru.models import Profile, User

USER_ARGS = [f.name for f in User._meta.get_fields()]

def get_model_attributes(model, atr_list):
    return ",".join(str(getattr(model, atr)) for atr in atr_list)

class Command(BaseCommand):
    help = 'Get user information for specified User or all Users'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str, help='User ID')
        parser.add_argument('group_name', type=str, help='Group Name')
        parser.add_argument('attributes', type=str, nargs='*')

    def handle(self, *args, **options):
        group_name = options.get('group_name')
        attributes = options.get('attributes')

        if not set(attributes) <= set(USER_ARGS):
            raise CommandError('Illegal attribute')

        try:
            if options.get('user_id') == 'all':
                for profile in Profile.objects.all().filter(group__name=group_name):
                    self.stdout.write(self.style.SUCCESS(get_model_attributes(profile.user, attributes)))
            else:
                try:
                    uid = int(options.get('user_id'))
                except ValueError as e:
                    raise CommandError('User ID must be an integer') from e
                profile = Profile.objects.filter(id=uid, group__name=group_name).first()
                self.stdout.write(self.style.SUCCESS(get_model_attributes(profile.user, attributes)))
        except (User.DoesNotExist, AttributeError) as exc:
            raise CommandError('User does not exist') from exc
