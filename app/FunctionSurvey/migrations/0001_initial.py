# Generated by Django 5.1.5 on 2025-02-06 02:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('return_type', models.TextField()),
                ('arguments', models.JSONField()),
                ('file', models.TextField()),
                ('line', models.IntegerField()),
                ('static', models.BooleanField(default=False)),
                ('const', models.BooleanField(default=False)),
                ('is_prototype', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'function',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='FunctionRelation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.TextField()),
                ('line', models.IntegerField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('call_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_from', to='FunctionSurvey.function')),
                ('call_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_to', to='FunctionSurvey.function')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='functioin_relation_project', to='FunctionSurvey.project')),
            ],
            options={
                'db_table': 'function_relation',
            },
        ),
        migrations.AddField(
            model_name='function',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='functioin_project', to='FunctionSurvey.project'),
        ),
    ]
