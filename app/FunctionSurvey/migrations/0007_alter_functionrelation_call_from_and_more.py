# Generated by Django 5.1.5 on 2025-03-26 05:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FunctionSurvey', '0006_function_include_do_function_include_for_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functionrelation',
            name='call_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='call_from', to='FunctionSurvey.function'),
        ),
        migrations.AlterField(
            model_name='functionrelation',
            name='call_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='call_to', to='FunctionSurvey.function'),
        ),
    ]
