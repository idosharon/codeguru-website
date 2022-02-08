from django.core.management.base import BaseCommand, CommandError
from codeguru.models import Profile, User

USER_ARGS = [f.name for f in User._meta.get_fields()]

def get_model_attributes(model, atr_list):
    return ",".join(str(getattr(model, atr)) for atr in atr_list)

class Command(BaseCommand):
    help = 'Get user information for specified User or all Users'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str)
        parser.add_argument('attributes', type=str, nargs='*')

    def handle(self, *args, **options):
        attributes = options.get('attributes')
        

        if not set(attributes) <= set(USER_ARGS):
            raise CommandError('Illegal attribute')
        
        try:
            if options.get('user_id') == 'all':
                for user in User.objects.all():
                    self.stdout.write(self.style.SUCCESS(get_model_attributes(user, attributes)))    
            else:
                try:
                    uid = int(options.get('user_id'))
                except ValueError:
                    raise CommandError('User ID must be an integer')
                user = User.objects.filter(id=uid).first()
                self.stdout.write(self.style.SUCCESS(get_model_attributes(user, attributes)))
        except (User.DoesNotExist, AttributeError):
            raise CommandError('User does not exist')
