from django.shortcuts import render
from rest_framework import  viewsets
from .models import Graph, Node, Edge, File, NodeTraversal
from .serializers import GraphSerializer, NodeSerializer, EdgeSerializer,\
    FileSerializer
from rest_framework import generics
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework import views, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from itertools import chain
from rest_framework.decorators import api_view
from django.db.models import Q, Max
import json
from django.http import JsonResponse

# Create your views here.


class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


class EdgeList(generics.ListCreateAPIView):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class EdgeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class GraphList(generics.ListCreateAPIView):
    queryset = Graph.objects.all()
    serializer_class = GraphSerializer


class GraphDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Graph.objects.all()
    serializer_class = GraphSerializer


@api_view(['GET'])
def get_groups(request, *args, **kwargs):
    """
    Returns list of nodes that form an island, and the position of the bounding rectangle
    :param request:
    :param args:
    :param kwargs: primary key of graph
    :return:
    """
    graph = get_object_or_404(Graph, pk=kwargs['graph_pk'])
    # node_traversal.traversed_nodes = set(chain(Node.objects.none(), Node.objects.none()))
    # node_traversal.nodes_to_traverse = Node.objects.none()
    groups = []

    start_node = graph.nodes.all()[0]
    explored = Node.objects.none()

    while start_node:
        node_traversal = NodeTraversal.objects.create()
        node_traversal.traversed_nodes.set(Node.objects.none())
        node_traversal.nodes_to_traverse.set(Node.objects.none())
        node_traversal.nodes_to_traverse.set(set(chain(node_traversal.nodes_to_traverse.all(),
                                                     connected_nodes(start_node))))
        node_traversal.traversed_nodes.set(set(chain(node_traversal.traversed_nodes.all(),
                                                     graph.nodes.filter(pk=start_node.pk))))
        while node_traversal.nodes_to_traverse.all().count() is not 0 :
            for node in node_traversal.nodes_to_traverse.all():

                node_traversal.nodes_to_traverse.set(node_traversal.nodes_to_traverse.union(connected_nodes(node)))
                node_traversal.nodes_to_traverse.set(node_traversal.nodes_to_traverse.all().difference(
                    node_traversal.traversed_nodes.filter(pk=node.pk)))
                if node not in node_traversal.traversed_nodes.all():
                    node_traversal.traversed_nodes.set(
                        node_traversal.traversed_nodes.all().union(graph.nodes.filter(pk=node.pk)))
        group = (node_traversal.traversed_nodes.all())
        groups.append(group)
        for group in groups:
            explored = (explored.union(group))
        unexplored = graph.nodes.all().difference(explored)
        if unexplored.count() == 0:
            start_node = None
        else:
            start_node = unexplored[0]



    group_list = []
    for group in groups:
        """
        Bounding Rectanngle is being located here. 
        """
        bounding_rectangle = {
            'top': group.aggregate(Max('top'))['top__max'],
            'left': group.aggregate(Max('left'))['left__max'],
            'bottom': group.aggregate(Max('bottom'))['bottom__max'],
            'right': group.aggregate(Max('right'))['right__max'],
            }

        group_list += ([NodeSerializer(group, many=True).data]) + [(bounding_rectangle)]
    return Response(group_list)


def connected_nodes(node):
    """
    Returns node connected to a node
    :param node: node in question
    :return: connected to the node in question
    """
    node_connected_to = Node.objects.none()
    for e in Edge.objects.filter(Q(source=node) | Q(target=node)):
        if e.source == node:
            node_connected_to = node_connected_to.union(Node.objects.filter(pk=e.target.pk))

    return node_connected_to


class WeaklyConnectedList(generics.ListAPIView):
    """
    Returns all “weakly connected” nodes for a graph on the server. A “weakly connected” node
is defined as a node which has no incoming edges with strength over 0.5.
    """
    serializer_class = NodeSerializer

    def get_queryset(self):
        graph = get_object_or_404(Graph, pk=self.kwargs['graph_pk'])
        return set([node for node in graph.nodes.all().iterator() if node.weakly_connected()])


class FileUploadView(views.APIView):
    """
    File upload to create node data from csv file.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            file_object = File.objects.last()
            graph = get_object_or_404(Graph, title=file_object.title)
            with open('/home/nk/Projects/mavenoid/graphservice/graphservice'+file_object.file.url, 'r') as f:
                for line in f:
                    l = line.replace("\n", "").split(',')
                    Node.objects.create(graph=graph, iid=l[0], title=l[1],
                                       top=float(l[2]), left=float(l[3]), bottom=float(l[4]), right=float(l[5]))
                f.close()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def nodes_with_incoming_edge_from_source_node_overlapped_by_rectangle(request, *args, **kwargs):
    """
    Given a rectangle specified in the request and a graph identifier, returns all nodes that have
    an incoming edge whose source node overlaps with that rectangle
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    graph = get_object_or_404(Graph, pk=kwargs['graph_pk'])
    top = float(request.data['top'])
    left = float(request.data['left'])
    bottom = float(request.data['bottom'])
    right = float(request.data['right'])
    all_overlapping_nodes = graph.nodes.filter(
        top__lte=top,
        left__lte=left,
        bottom__lte=bottom,
        right__lte=right
    )                                # This will filter all nodes that are inside the given rectangle
    node_with_incoming_edge = Node.objects.none()     # empty queryset initialized
    for node in all_overlapping_nodes.iterator():
        edge_with_source_node_overlapped = Edge.objects.filter(source=node)  # filter all edges from a node in all overlapping nodes
        for edge in edge_with_source_node_overlapped:
            node_with_incoming_edge\
                = set(chain(node_with_incoming_edge,
                            Node.objects.filter(pk=edge.target.pk)))        # filters required node having incoming edge from node

    serializer = NodeSerializer(node_with_incoming_edge, many=True)
    return Response(serializer.data)



