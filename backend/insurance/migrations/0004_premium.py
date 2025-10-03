# Generated migration for Premium model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0003_buyer_is_active_buyer_last_login_buyer_password_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Premium',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_hash', models.CharField(max_length=66, unique=True)),
                ('amount_eth', models.DecimalField(decimal_places=18, max_digits=30)),
                ('amount_wei', models.CharField(max_length=100)),
                ('block_number', models.BigIntegerField()),
                ('block_timestamp', models.DateTimeField()),
                ('gas_used', models.BigIntegerField(blank=True, null=True)),
                ('gas_price', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')], default='confirmed', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premiums', to='insurance.buyer')),
                ('policy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='insurance.policy')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]