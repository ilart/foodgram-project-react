# Generated by Django 2.2.16 on 2022-04-14 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220412_0712'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TagsInRecipe',
            new_name='TagInRecipe',
        ),
    ]
