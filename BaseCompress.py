import leidenalg
import igraph as ig

import networkx as nx


class BaseCompress():
    def reduce_graph(self, G: nx.DiGraph, result: list, cutoff=5000):
        if len(G.edges) <= cutoff:
            result.append(G)
        else:
            G_ig = ig.Graph.from_networkx(G.copy())
            part = leidenalg.find_partition(G_ig, leidenalg.ModularityVertexPartition)

            for p in part:
                nodes = list(p)

                if len(nodes) > 5:
                    G_sub = G.subgraph(nodes)
                    if len(G_sub.edges) > 10:
                        self.reduce_graph(G_sub, result)

    def transform_perm(self, e, c_perm):
        if e not in c_perm:
            return e

        i = c_perm.index(e)
        i += 1
        if i >= len(c_perm):
            i = 0

        return c_perm[i]

    def transform_perms_single_cycle(self, e, c_perm):
        ne = []
        edge = e

        for _ in range(len(c_perm)):
            ne.append((self.transform_perm(edge[0], c_perm), self.transform_perm(edge[1], c_perm)))
            edge = (self.transform_perm(edge[0], c_perm), self.transform_perm(edge[1], c_perm))

        return ne

    def transform_perms_cycles(self, e, c_perms):
        new_edges = []
        curr_edge = e

        while True:
            ne = []

            for element in list(curr_edge):
                is_in = False

                for p in c_perms:
                    if element in p:
                        ne.append(self.transform_perm(element, p))
                        is_in = True

                if not is_in:
                    ne.append(element)

            if tuple(ne) in new_edges:
                break

            new_edges.append(tuple(ne))
            curr_edge = tuple(ne)

        return new_edges

    def transform_perms(self, e, c_perms):
        if len(c_perms) == 1:
            return self.transform_perms_single_cycle(e, c_perms[0])

        return self.transform_perms_cycles(e, c_perms)
