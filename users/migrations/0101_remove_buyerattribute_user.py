# Generated by Django 5.1.1 on 2025-07-17 17:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0100_introductionmethod_buyerattribute_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyerattribute',
            name='user',
        ),
    ]
