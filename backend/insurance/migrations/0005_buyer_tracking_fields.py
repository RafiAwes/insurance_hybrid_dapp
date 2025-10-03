# Generated migration for Buyer model updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0004_premium'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='total_premiums_paid',
            field=models.DecimalField(decimal_places=18, default=0, max_digits=30),
        ),
        migrations.AddField(
            model_name='buyer',
            name='last_premium_payment',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='premium_payment_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='buyer',
            name='claim_documents',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='buyer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]