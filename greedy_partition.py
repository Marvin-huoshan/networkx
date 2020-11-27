import networkx as nx
import numpy as np
from collections import defaultdict


class greed_arith:


    def __init__(self, G, k):
        self.G = G  # 图
        self.k = k
        self.degree_dict = {[i for i in G.nodes][n]: [len(G[i]) for i in G.nodes][n] for n in range(len(G.nodes()))} # 获得度列表
        self.group = defaultdict(set)
        self.degree_dict = dict(sorted(self.degree_dict.items(), key=lambda x: x[1], reverse=True))
        self.nodelist = list(self.degree_dict.keys())
        #  选择初始组
        self.distrib_node = list(self.degree_dict.keys())[0:self.k]

    def get_highest_degree(self):
        """

        :return:the max degree of nodelist
        """
        degree_list = [self.degree_dict[i] for i in self.distrib_node]
        max_degree = np.max(degree_list)
        return max_degree

    def show(self):
        print("图:", self.G)
        print("K值:", self.k)
        print("度字典:", self.degree_dict)
        # print("组:", self.distrib_node)

    def count_I(self,i,j):
        """
        :param i:the node index i
        :param j: the node index j
        :return: I(d[i,j])
        """
        d = self.degree_dict[self.nodelist[i]]
        result = 0
        print(self.nodelist)
        print(self.nodelist[i:j+1])
        print(self.distrib_node)
        for i in self.nodelist[i:j+1]:
            result += d - self.degree_dict[self.nodelist[i]]
        return result

    def count_diff_d(self,i,j):
        """
        :param i:the node index i
        :param j: the node index j
        :return: the differencce of degree
        """
        di = self.degree_dict[self.nodelist[i]]
        dj = self.degree_dict[self.nodelist[j]]
        return di - dj

    def run(self):
        for i in range(self.k, len(self.nodelist)):

            if self.nodelist[i] in self.distrib_node:
                continue
            try:
                cmerge = (self.get_highest_degree() - self.degree_dict[self.nodelist[i]]) + self.count_I(i+1, i + 1 + self.k)
            except:
                self.distrib_node.append(self.nodelist[i])
            cnew = (self.count_I(i, i + self.k))
            if cmerge > cnew:
                print("组", self.distrib_node)
                self.distrib_node = self.nodelist[i : i + self.k ]
            if cmerge < cnew:
                self.distrib_node.append(self.nodelist[i])
                # print('组：', self.distrib_node, '，加入点：', self.nodelist[i])

        print("组",self.distrib_node)


if __name__ == '__main__':
    G = nx.karate_club_graph()
    k = 3
    h = greed_arith(G, k)
    h.show()
    h.run()

