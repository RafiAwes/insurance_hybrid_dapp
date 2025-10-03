from django.core.management.base import BaseCommand
from insurance.models import Buyer

class Command(BaseCommand):
    help = 'Create a buyer user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Buyer email address', required=True)
        parser.add_argument('--password', type=str, help='Buyer password', required=True)
        parser.add_argument('--name', type=str, help='Buyer full name', required=True)
        parser.add_argument('--wallet', type=str, help='Buyer wallet address', required=True)
        parser.add_argument('--national-id', type=str, help='Buyer national ID', required=True)
        parser.add_argument('--phone', type=str, help='Buyer phone number', default='')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        full_name = options['name']
        wallet_address = options['wallet']
        national_id = options['national_id']
        phone = options['phone']

        # Validate wallet address format
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            self.stdout.write(
                self.style.ERROR('Invalid wallet address format. Must be 42 characters starting with 0x')
            )
            return

        # Check if buyer already exists
        if Buyer.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Buyer with email {email} already exists')
            )
            return

        if Buyer.objects.filter(wallet_address=wallet_address).exists():
            self.stdout.write(
                self.style.WARNING(f'Buyer with wallet address {wallet_address} already exists')
            )
            return

        if Buyer.objects.filter(national_id=national_id).exists():
            self.stdout.write(
                self.style.WARNING(f'Buyer with national ID {national_id} already exists')
            )
            return

        # Create buyer
        buyer = Buyer(
            email=email,
            full_name=full_name,
            wallet_address=wallet_address,
            national_id=national_id,
            phone=phone,
            is_active=True
        )
        buyer.set_password(password)
        buyer.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created buyer: {email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Name: {full_name}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Wallet: {wallet_address}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Buyer ID: {buyer.id}')
        )
        self.stdout.write(
            self.style.WARNING(f'Remember to use wallet address {wallet_address} for MetaMask verification')
        )