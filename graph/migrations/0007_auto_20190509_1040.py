# Generated by Django 2.2.1 on 2019-05-09 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0006_auto_20190508_2012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graph',
            name='edges',
        ),
        migrations.RemoveField(
            model_name='graph',
            name='nodes',
        ),
        migrations.AddField(
            model_name='edge',
            name='graph',
            field=models.ManyToManyField(related_name='graph_edges', to='graph.Graph'),
        ),
        migrations.AddField(
            model_name='graph',
            name='edge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edge_in_graph', to='graph.Edge'),
        ),
        migrations.AddField(
            model_name='graph',
            name='node',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='node_in_graph', to='graph.Node'),
        ),
        migrations.AddField(
            model_name='node',
            name='graph',
            field=models.ManyToManyField(related_name='nodes', to='graph.Graph'),
        ),
    ]
