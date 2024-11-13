from django.core.management.base import BaseCommand
from django.utils import timezone
from AppCodingNexus.models import UserProfile

class Command(BaseCommand):
    help = 'Delete user accounts that have been marked for deletion for more than 30 days'

    def handle(self, *args, **kwargs):
        profiles = UserProfile.objects.filter(
            is_deleted=True,
            deletion_requested__lt=timezone.now() - timezone.timedelta(days=30)
        )
        
        count = 0
        for profile in profiles:
            user = profile.user
            user.delete()  # This will cascade delete the profile as well
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired accounts')
        ) 