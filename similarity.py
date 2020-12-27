import networkx as nx
from networkx import Graph
import matplotlib.pyplot as plt
import xlsxwriter
import xlrd
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool,Process
from multiprocessing.managers import BaseManager
import pandas as pd
import random
import os

def avg_cluster(G):
    '''计算图的平均聚类系数'''
    return nx.average_clustering(G)

def avg_shortest_path(G):
    '''计算图的平均最短路径长度'''
    return nx.average_shortest_path_length(G)

def avg_betweenness_change(G1,G2):
    '''计算betweenness的平均改变量'''
    sum1 = 0;sum2 = 0
    dict1 = nx.betweenness_centrality(G1)
    dict2 = nx.betweenness_centrality(G2)
    #print(dict1)
    #print(dict2)
    for val1 in dict1.values():
        sum1 += val1
    for val2 in dict2.values():
        sum2 += val2
    return (sum1-sum2)/sum1

if __name__ == '__main__':

    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    G_1 = nx.read_gml('1.gml', label=None)
    G_HepTh = nx.read_edgelist('CA-HepTh.txt')
    G_HepTh = nx.convert_node_labels_to_integers(G_HepTh)
    G_HepPh = nx.read_edgelist('CA-HepPh.txt')
    G_HepPh = nx.convert_node_labels_to_integers(G_HepPh)
    G_kar_un = G_kar.to_undirected()
    G_1_un = G_1.to_undirected()
    G_1_anoy_1 = nx.read_gml('1-sheet1.gml')
    G_1_anoy_2 = nx.read_gml('1-sheet2.gml')
    G_1_anoy_3 = nx.read_gml('1-sheet3.gml')
    G_1_anoy_4 = nx.read_gml('1-sheet4.gml')
    G_kar_anoy_1 = nx.read_gml('kar-sheet1.gml')
    G_kar_anoy_2 = nx.read_gml('kar-sheet2.gml')
    G_kar_anoy_3 = nx.read_gml('kar-sheet3.gml')
    G_kar_anoy_4 = nx.read_gml('kar-sheet4.gml')
    print(2*nx.number_of_edges(G_kar)/nx.number_of_nodes(G_kar))
    print(2*nx.number_of_edges(G_kar_anoy_1)/nx.number_of_nodes(G_kar_anoy_1))
    print(2 * nx.number_of_edges(G_1) / nx.number_of_nodes(G_1))
    print(2 * nx.number_of_edges(G_1_anoy_1) / nx.number_of_nodes(G_1_anoy_1))
    print('{:.2%}'.format((avg_cluster(G_1)-avg_cluster(G_1_anoy_1))/avg_cluster(G_1)))
    print('{:.2%}'.format((avg_shortest_path(G_1) - avg_shortest_path(G_1_anoy_1)) / avg_shortest_path(G_1)))
    print('{:.2%}'.format(avg_betweenness_change(G_1,G_1_anoy_1)))
    print(avg_cluster(G_1))
    print(avg_cluster(G_1_anoy_1))
    print(avg_shortest_path(G_1))
    print(avg_shortest_path(G_1_anoy_1))