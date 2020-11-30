import networkx as nx
import matplotlib.pyplot as plt
import xlsxwriter
import xlrd
import numpy as np
import time

def find_max_graph(G,list1):
    '''寻找分为一类的节点中，一邻居子图节点个数最多的节点id'''
    list_copy = []
    for i in list1:
        neighbor_list = list(nx.all_neighbors(G,i))
        list_copy.append(len(neighbor_list) + 1)
    a = max(list_copy)
    b = list_copy.index(a)
    c = list1[b]
    return c

def read_class(G,file):
    workbook = xlrd.open_workbook(file)
    mySheet1 = workbook.sheet_by_name('Sheet1')
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    nrows = mySheet1.nrows
    for i in range(1,nrows):
        list1 = [i for i in list(mySheet1.row_values(i)) if i != '']
        max = find_max_graph(G,list1)   #找出每一个类最大的那个子图
        list1.remove(max)
        for i in list1:
            find_OEP_with(G,i,max)

def find_OEP_with(G,node1,node2):
    list1 = list(nx.all_neighbors(G,node1))
    list2 = list(nx.all_neighbors(G,node2))
    list1.append(node1)
    list2.append(node2)
    #创建节点的一邻居子图（包含自己）
    subgraph1 = nx.subgraph(G,list1)
    subgraph2 = nx.subgraph(G,list2)
    nx.optimal_edit_paths(subgraph1,subgraph2)



if __name__ == '__main__':
    t0 = time.perf_counter()
    G_1 = nx.read_gml('1.gml')
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    #read_class(G_1,'com-part-com-3anoymous-1-3-rdivision.xlsx')
    list1 = list(nx.all_neighbors(G_1,'71'))
    list1.append('71')
    #print(list1)
    subgraph1 = nx.subgraph(G_1,list1)
    list2 = list(nx.all_neighbors(G_1,'305'))
    list2.append('305')
    #print(list2)
    subgraph2 = nx.subgraph(G_1,list2)
    #print(nx.graph_edit_distance(subgraph1,subgraph2))
    print(list(nx.optimize_edit_paths(subgraph1,subgraph2,timeout=60)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=120)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=180)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=240)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=300)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=3600)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=4200)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=6000)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=12000)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=18000)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=24000)))
    print(list(nx.optimize_edit_paths(subgraph1, subgraph2, timeout=30000)))
    #print(list(nx.optimize_edit_paths(subgraph1, subgraph2)))


    #print(nx.optimal_edit_paths(subgraph1,subgraph2))
    print(time.perf_counter() - t0)
    #print(nx.number_of_edges(subgraph2))
