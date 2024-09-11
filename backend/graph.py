#https://stackoverflow.com/questions/19472530/representing-graphs-data-structure-in-python

#Graph to store scores and graph connections object with graph operations, stores graph as dict and performs operations on it
class Graph(object):
    #Initialise graph object and set scores
    def __init__(self, graph, scores):
        if graph is None:
            graph = {}
        self._graph = graph
        if scores is None:
            scores = {}
        self._scores = scores

    #If graph object is passed, set the class graph property to the passed object
    def resume_graph(self, graph):
        self._graph = graph

    #If score object passed, set score of class to this object
    def firstsetscore(self, title):
        self._scores[title] = 0

    #Return graph dict
    def graph(self):
        return self._graph
    
    #Return score dict
    def scores(self):
        return self._scores

    #Return score for given paper, if none, throw key error
    def fetch_score(self, paper):
        try:
            return self._scores[paper]
        except KeyError:
            pass

    #Update score of given node, set score to passed score
    def update_score(self, score, paper):
        self._scores[paper]=score

    #Remove score and paper if paper is removed (only called manually if needed)
    def remove_score(self, paper):
        try:
            del self._scores[paper]
        except KeyError:
            pass
    
    #Add node to graph object
    def add(self, origin, connection):
        if origin not in self._graph:
            self._graph[origin] = []
        if connection:
            self._graph[origin].append(connection)
            self._graph[connection].append(origin)
    
    #Remove paper and connections if possible (only called manually for debugging)
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
    
    #Return connections of root node
    def findconnections(self, origin):
        return self._graph[origin]
    
    #Ensure string representation of object is returned
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))