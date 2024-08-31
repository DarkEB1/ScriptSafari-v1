#https://stackoverflow.com/questions/19472530/representing-graphs-data-structure-in-python
from collections import defaultdict

class Graph(object):
    def __init__(self, graph, scores):
        self._graph = graph
        self._scores = scores

    def resume_graph(self, graph):
        self._graph = graph

    def firstsetscore(self, title):
        self._scores[title] = 0

    def graph(self):
        return self._graph
    
    def scores(self):
        return self._scores

    def fetch_score(self, paper):
        try:
            return self._scores[paper]
        except KeyError:
            pass

    def update_score(self, score, paper):
        self._scores[paper]=score

    def remove_score(self, paper):
        try:
            del self._scores[paper]
        except KeyError:
            pass
    
    def add(self, origin, connection):
        self._graph[origin].add(connection)
        self._graph[connection].add(origin)
    
    def remove(self, removed):
        for paper, connections in self._graph.items():
            try:
                connections.remove(removed)
            except KeyError:
                pass
        try:
            del self._graph[removed]
        except KeyError:
            pass
    
    def findconnections(self, origin):
        return self._graph[origin]
        
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))