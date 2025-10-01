from django.core.management.base import BaseCommand
from myapp.models import Buyer, Policy

class Command(BaseCommand):
    help = 'Seed initial data for the health insurance app'

    def handle(self, *args, **options):
        # Create sample buyer
        buyer, created = Buyer.objects.get_or_create(
            wallet_address='0x742d35Cc6f1B1d3b3F1a7bB8e5d4a2c6b3e8f9a1',
            defaults={
                'national_id': 'NID123456789',
                'full_name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1-555-0123',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created buyer: {buyer.full_name}'))
        else:
            self.stdout.write(f'Buyer already exists: {buyer.full_name}')

        # Create sample policy for the buyer
        policy, created = Policy.objects.get_or_create(
            buyer=buyer,
            defaults={
                'policy_number': 'POL-001',
                'monthly_premium': 100.00,
                'status': 'active',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created policy: {policy.policy_number}'))
        else:
            self.stdout.write(f'Policy already exists: {policy.policy_number}')

        self.stdout.write(self.style.SUCCESS('Seed data completed!'))