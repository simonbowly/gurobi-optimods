import logging


class Grbgraph:
    """
    Simple network graph class to hold necessary edge and vertex information.
    """

    def __init__(self):
        self.vertices = {}
        self.edges = {}
        self.n = 0  # number of vertices
        self.m = 0  # number of edges
        logger = logging.getLogger("OpfLogger")
        logger.info("Created Grbgraph object.")

    def addvertex(self, i):
        """
        Adds a vertex to the Graph

        Parameters
        ----------
        i : int
            vertex index
        """
        self.vertices[self.n] = i
        self.n += 1

    def addedge(self, i, j):
        """
        Adds an edge to the Graph

        Parameters
        ----------
        i : int
            vertex index of first node
        j : int
            vertex index of second node
        """
        if i in self.vertices.values() and j in self.vertices.values():
            self.edges[self.m] = (i, j)
            self.m += 1
            return 0
        else:
            return 1

    def getmetrics(self):
        """
        Prints graph statistics
        """
        logger = logging.getLogger("OpfLogger")
        logger.info("Graph object has %d vertices %d edges." % (self.n, self.m))
