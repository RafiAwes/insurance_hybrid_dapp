from django.core.management.base import BaseCommand
from django.conf import settings
from insurance.event_listener import listen_to_events

class Command(BaseCommand):
    help = 'Start the blockchain event listener'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting blockchain event listener...')
        )
        try:
            listen_to_events()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Event listener stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Event listener crashed: {str(e)}')
            )