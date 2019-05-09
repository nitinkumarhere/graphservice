from rest_framework import serializers
from .models import Graph, Node, NodePosition,  Edge
from rest_framework.parsers import JSONParser


class NodePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodePosition
        fields = ('top', 'left', 'bottom', 'right')


class NodeSerializer(serializers.ModelSerializer):
    position = NodePositionSerializer(many=True)

    class Meta:
        model = Node
        fields = ('iid', 'title', 'position')


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = ('source', 'target')


class GraphSerializer(serializers.ModelSerializer):
    nodes = NodeSerializer(many=True)
    edges = EdgeSerializer(many=True)

    class Meta:
        model = Graph
        fields = ('title', 'nodes', 'edges')

    def create(self, validated_data):
        node_data = validated_data.pop('node')
        edge_data = validated_data.pop('edge')

        for node_data in node_data:
            position_data = node_data.pop('position')
            node = Node.objects.create(**node_data)

            NodePosition.objects.create(node=node, **position_data)
        for edge_data in edge_data:
            Edge.objects.create(**edge_data)
        graph = Graph.objects.create(**validated_data)
        return graph



