# Generated by Django 3.0.8 on 2021-02-04 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_mappool'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='competitions',
            field=models.ManyToManyField(blank=True, related_name='maps', to='core.Competition'),
        ),
    ]
