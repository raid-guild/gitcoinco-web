# Generated by Django 2.1.5 on 2019-03-10 14:08

from django.db import migrations, models
import django.db.models.deletion
import economy.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_merge_20190307_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundFeeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('fulfilled', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, max_length=500)),
                ('comment_admin', models.TextField(blank=True, max_length=500)),
                ('fee_amount', models.FloatField()),
                ('token', models.CharField(max_length=10)),
                ('address', models.CharField(max_length=50)),
                ('txnId', models.CharField(blank=True, max_length=50)),
                ('bounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Bounty')),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refund_requests', to='dashboard.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]