from django.core.management.base import BaseCommand
from insurance.models import Admin

class Command(BaseCommand):
    help = 'Create an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email address', required=True)
        parser.add_argument('--password', type=str, help='Admin password', required=True)
        parser.add_argument('--name', type=str, help='Admin full name', required=True)

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        full_name = options['name']

        # Check if admin already exists
        if Admin.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin with email {email} already exists')
            )
            return

        # Create admin
        admin = Admin(
            email=email,
            full_name=full_name,
            is_active=True
        )
        admin.set_password(password)
        admin.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin: {email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Name: {full_name}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Admin ID: {admin.id}')
        )
        self.stdout.write(
            self.style.WARNING('Remember to use the admin wallet address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266')
        )