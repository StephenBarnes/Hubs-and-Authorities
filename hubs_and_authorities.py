#!/usr/bin/env python2

import graphviz as gv
import itertools as it
import random

def standardize(L):
    s = sum(L)
    return [l / s for l in L]

class Node:
    def __init__(self, name):
        self.name = name
        self.out = set()
        self.inn = set()
        self.hubbiness = 1.
        self.authority = 1.
    def new_hubbiness(self):
        return sum(n.authority for n in self.out) + 1.
    def new_authority(self):
        return sum(n.hubbiness for n in self.inn) + 1.
    def color(self, maxhub, maxauth, minhub, minauth):
        red_frac = (self.hubbiness - minhub) / (maxhub - minhub)
        green_frac = (self.authority - minauth) / (maxauth - minauth)
        red_comp = hex(int(0xFF * red_frac))[2:].rjust(2, '0')
        green_comp = hex(int(0xFF * green_frac))[2:].rjust(2, '0')
        return "#%s%s00" % (red_comp, green_comp)

class Graph:
    def __init__(self):
        self.nodes = []
    def add_edge(self, i_node, j_node):
        n1, n2 = self.nodes[i_node], self.nodes[j_node]
        n1.out.add(n2)
        n2.inn.add(n1)
    def update_ha(self):
        maxchange = 0.
        new_h, new_a = [], []
        for node in self.nodes:
            new_h.append(node.new_hubbiness())
            new_a.append(node.new_authority())
        new_h = standardize(new_h)
        new_a = standardize(new_a)
        for nh, na, node in zip(new_h, new_a, self.nodes):
            maxchange = max(maxchange, abs(node.hubbiness - nh))
            maxchange = max(maxchange, abs(node.authority - nh))
            node.hubbiness = nh
            node.authority = na
        return maxchange
    def solve_for_ha(self, threshold = 0.001, maxiters = 300):
        for i in xrange(maxiters):
            change = self.update_ha()
            print change
            if change < threshold:
                return
    def draw_ha_joint(self):
        from matplotlib import pyplot as plt
        hubbinesses = [n.hubbiness for n in self.nodes]
        authorities = [n.authority for n in self.nodes]
        plt.plot(hubbinesses, authorities, 'o')
        plt.show()
        raw_input()
    def draw(self):
        G = gv.Digraph()
        maxhub = max(n.hubbiness for n in self.nodes)
        maxauth = max(n.authority for n in self.nodes)
        minhub = min(n.hubbiness for n in self.nodes)
        minauth = min(n.authority for n in self.nodes)
        for n in self.nodes:
            color = n.color(maxhub, maxauth, minhub, minauth)
            G.node(str(n.name), style='filled', color=color)
        for n in self.nodes:
            for out in n.out:
                G.edge(str(n.name), str(out.name))
        G.format = 'svg'
        G.engine = 'neato'
        G.render('/tmp/ha.gv', view=True)

def random_graph_fixed_p(n_vertices, p_edge):
    G = Graph()
    for i in xrange(n_vertices):
        G.nodes.append(Node(name=i))
    for i, j in it.combinations(range(n_vertices), 2):
        if random.random() < p_edge:
            G.add_edge(i, j)
    return G

def random_multichoice(L, n, forbidden=None):
    assert len(L) >= n
    R = set()
    while len(R) < n:
        x = random.choice(L)
        if forbidden is None or x == forbidden:
            continue
        R.add(x)
    return R

def random_graph_by_outdegree(n_vertices, outdegree_func):
    G = Graph()
    vertex_indices = range(n_vertices)
    for i in vertex_indices:
        G.nodes.append(Node(name=i))
    for i, n in enumerate(G.nodes):
        outdegree = outdegree_func()
        out_indices = random_multichoice(vertex_indices, outdegree, forbidden=i)
        for out_index in out_indices:
            G.add_edge(i, out_index)
    return G


outdegree_func = lambda: random.choice(
        [0] * 10
        + [1] * 20
        + [2] * 5
        + [3] * 2
        )
Network = random_graph_by_outdegree(150, outdegree_func)
Network.solve_for_ha()
Network.draw()
Network.draw_ha_joint()
