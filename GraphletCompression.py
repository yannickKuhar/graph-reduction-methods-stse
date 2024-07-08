import itertools
import networkx as nx
from networkx.algorithms import isomorphism as iso

from BaseCompress import BaseCompress


class GraphletCompression(BaseCompress):

    def __init__(self, digraph_file="graphlets_re.txt"):
        self.digraph_file = digraph_file

    def get_all_subgraphs(self, G, n):
        for SG in (G.subgraph(selected_nodes) for selected_nodes in itertools.combinations(G, n)):
            if nx.is_weakly_connected(SG):
                yield SG

    def digraphs(self, file):
        with open(file, "r") as f:
            for line in f.readlines():
                format = line.split("|")

                G = nx.DiGraph()

                for edge in format[0].split(" "):
                    e = edge.split(",")
                    G.add_edge(int(e[0]), int(e[1]))

                yield G, format[0], format[1], format[2]

    def map_edges(self, rev_map, edge_string):
        result = ""

        for edge in edge_string.split(" "):
            u, v = edge.split(",")

            result += f"{rev_map[int(u)]},{rev_map[int(v)]} "

        return result.strip()

    def rev_map_sym(self, rev_map, sym):
        result = ""

        for s in sym.split(" "):
            tmp = s.split(",")

            for x in tmp:
                result += f"{rev_map[int(x)]},"

            result = result[:-1] + " "

        return result.strip()

    def map_sym(self, rev_map, sym):
        sym_split = sym.split(" ")

        if len(sym_split) == 1:
            result = ""

            for s in sym.split(","):
                result += f"{rev_map[int(s)]},"

            return result[:-1]
        elif len(sym_split) > 1:
            return self.rev_map_sym(rev_map, sym)
        else:
            raise Exception(f"Len {len(sym_split)} of {sym_split} is incompatible.")

    def compress(self, G: nx.DiGraph, name):
        G_tmp = G.copy()

        comp_gp = []
        comp_eg = []

        result = []
        self.reduce_graph(G, result, cutoff=30000)

        for i, g in enumerate(result):
            print(f"{i + 1}/{len(result)}")
            print(g)

            gp, eg = self.compress_subg(g)
            comp_gp += gp
            comp_eg += eg

            for u, v in g.edges:
                G_tmp.remove_edge(u, v)

        with open(f"{name}_compressed.graph", "w+", encoding="ascii") as f:
            f.write(f"{len(G)}\n")

            for gp in list(set(comp_gp)):
                f.write(gp)

            f.write("*\n")

            for eg in comp_eg:
                f.write(eg)

            for u, v in G_tmp.edges:
                f.write(f"{u} {v}\n")

    def compress_subg(self, G: nx.DiGraph):
        comp_gp = []
        comp_eg = []

        G_tmp = G.copy()

        i = 1

        for g, g_str, g_res, sym in self.digraphs(self.digraph_file):

            print(f"Graphlets: {i} / 93921")

            dm = iso.DiGraphMatcher(G_tmp, g)

            while dm.subgraph_is_isomorphic():
                rev_map = {v: k for k, v in dm.mapping.items()}

                gr = ""
                for edge in g_res.split(" "):
                    u, v = edge.split(",")
                    gr += f"{rev_map[int(u)]},{rev_map[int(v)]} "

                for u, v in g.edges():
                    G_tmp.remove_edge(rev_map[u], rev_map[v])

                print(f"{len(G_tmp.edges)} / {len(G.edges)}")

                comp_gp.append(f"{gr.strip()}:{self.map_sym(rev_map, sym)}\n")

                dm = iso.DiGraphMatcher(G_tmp, g)

            i += 1

        for e in G_tmp.edges():
            comp_eg.append(f"{e[0]} {e[1]}\n")

        return comp_gp, comp_eg

    def reconstruct(self, g_res, sym):
        result_edges = []

        edges = []
        symmetry = []

        for edge in g_res.strip().split(" "):
            e = list(map(int, edge.split(",")))
            edges.append((e[0], e[1]))

        for s in sym.strip().split(" "):
            tmp = list(map(int, s.split(",")))
            symmetry.append(tuple(tmp))

        for edge in edges:
            ne1 = self.transform_perms_decomp(edge, symmetry)
            if isinstance(ne1, list):
                if len(ne1) == 2 and isinstance(ne1[0], int):
                    result_edges.append(tuple(ne1))
                else:
                    for e in ne1:
                        result_edges.append(e)
            else:
                result_edges.append(ne1)

        return list(set(result_edges))

    def decompress(self, f_comp, starting_node=0):
        G = nx.DiGraph()

        nums = 1

        with open(f_comp, "r") as f:
            n = int(f.readline())
            G.add_nodes_from(range(starting_node, n + starting_node))

            for line in f:
                if line.startswith("*"):
                    break

                g_residual, sym = line.split(":")

                nums += len(g_residual.split(" ")) * 2
                for s in sym.split(" "):
                    nums += len(s.split(","))

                for u, v in self.reconstruct(g_residual, sym):
                    G.add_edge(u, v)

            for line in f:
                u, v = line.split(" ")
                G.add_edge(int(u), int(v))
                nums += 2

        return G, nums

    def adj_to_edge_string(self, adj_string):
        edges = []
        adjs = adj_string.split(" ")

        for adj in adjs:
            n, neighbors = adj.split(":")

            for node in neighbors.split(","):
                edges.append(f"{n},{node}")

        return " ".join(edges)

    def decompress_adj(self, sym_list, edge_list, starting_node=0):
        G = nx.DiGraph()
        nums = 1

        with open(sym_list, "r") as f:
            lines = f.readlines()
            n = int(lines[0])
            G.add_nodes_from(range(starting_node, n + starting_node))

            for line in lines[1:]:
                g_residual, sym = line.split("|")

                for s in sym.split(" "):
                    nums += len(s.split(","))

                g_residual = self.adj_to_edge_string(g_residual)
                nums += len(g_residual.split(" ")) * 2

                for u, v in self.reconstruct(g_residual, sym):
                    G.add_edge(u, v)

        with open(edge_list, "r") as f:
            for line in f.readlines():
                u, v = line.split(" ")
                G.add_edge(int(u), int(v))
                nums += 2

        return G, nums
