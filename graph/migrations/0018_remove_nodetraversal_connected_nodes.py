# Generated by Django 2.2.1 on 2019-05-16 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0017_nodetraversal_connected_nodes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nodetraversal',
            name='connected_nodes',
        ),
    ]
