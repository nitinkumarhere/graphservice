# Generated by Django 2.2.1 on 2019-05-09 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0010_auto_20190509_1050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edge',
            name='destination',
        ),
        migrations.AddField(
            model_name='edge',
            name='target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_target', to='graph.Node'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_source', to='graph.Node'),
        ),
    ]