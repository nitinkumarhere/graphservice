# Generated by Django 2.2.1 on 2019-05-08 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nodeposition',
            name='node',
        ),
        migrations.AddField(
            model_name='node',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_position', to='graph.NodePosition'),
        ),
    ]
