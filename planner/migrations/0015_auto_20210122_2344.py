# Generated by Django 3.1.3 on 2021-01-22 15:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0014_auto_20210118_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyexpense',
            name='category',
            field=models.CharField(default='Groceries', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='dailyexpense',
            name='type',
            field=models.CharField(default='Expense', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 22, 23, 44, 47, 265066)),
        ),
    ]
