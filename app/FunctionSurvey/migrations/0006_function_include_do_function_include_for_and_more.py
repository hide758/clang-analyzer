# Generated by Django 5.1.5 on 2025-03-18 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FunctionSurvey', '0005_function_end_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='function',
            name='include_do',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='function',
            name='include_for',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='function',
            name='include_if',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='function',
            name='include_switch',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='function',
            name='include_while',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
