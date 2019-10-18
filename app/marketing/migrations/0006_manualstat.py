# Generated by Django 2.2.3 on 2019-09-26 17:34

from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0005_marketingcallback'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('key', models.CharField(db_index=True, max_length=50)),
                ('date', models.DateTimeField(db_index=True)),
                ('val', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]