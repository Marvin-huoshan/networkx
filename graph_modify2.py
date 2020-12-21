import networkx as nx
from networkx import Graph
import matplotlib.pyplot as plt
import xlsxwriter
import xlrd
import numpy as np
import time
from tqdm import tqdm
from multiprocessing import Pool,Process
from multiprocessing.managers import BaseManager
import pandas as pd
import random
import os

def Adjacency(G):
    '''根据输入图，生成邻接矩阵、仅二跳可达矩阵、仅三跳可达矩阵,矩阵按照G.nodes()的顺序'''
    A = np.array(nx.adjacency_matrix(G).todense())  # 邻接矩阵
    A2s = np.dot(A, A)  # A2s
    row, col = np.diag_indices_from(A2s)
    A2s[row, col] = 0  # 对角线归零
    A2s[np.nonzero(A2s)] = 1  # 非零值为1
    A2 = A2s - A
    A2[A2 < 0] = 0  # 仅二跳可达矩阵
    A3s = np.dot(A2s, A)
    row, col = np.diag_indices_from(A3s)
    A3s[row, col] = 0  # 对角线归零
    A3s[np.nonzero(A3s)] = 1  # 非零值归1
    A3 = A3s - A2s
    A3[A3 < 0] = 0  # 仅三跳可达矩阵
    return A,A2,A3

def read_file(G,file):
    '''lists中存储了四个sheet的不同类，每一个小list按照度排序'''
    workbook = xlrd.open_workbook(file)
    mySheet1 = workbook.sheet_by_name('Sheet1')
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    lists = []
    for i in range(1, mySheet1.nrows):
        tmp_list1 = [i for i in list(mySheet1.row_values(i)) if i != '']
        tmp_list1 = sorted(tmp_list1,key=lambda x:nx.degree(G,x),reverse=True)
        list1.append(tmp_list1)
        tmp_list2 = [i for i in list(mySheet2.row_values(i)) if i != '']
        tmp_list2 = sorted(tmp_list2, key=lambda x: nx.degree(G, x), reverse=True)
        list2.append(tmp_list2)
        tmp_list3 = [i for i in list(mySheet3.row_values(i)) if i != '']
        tmp_list3 = sorted(tmp_list3, key=lambda x: nx.degree(G, x), reverse=True)
        list3.append(tmp_list3)
        tmp_list4 = [i for i in list(mySheet4.row_values(i)) if i != '']
        tmp_list4 = sorted(tmp_list4, key=lambda x: nx.degree(G, x), reverse=True)
        list4.append(tmp_list4)
    lists.append(list1)
    lists.append(list2)
    lists.append(list3)
    lists.append(list4)
    return lists

def do_by_graph(G,file,num,name):
    '''处理一个graph里面的每一个节点'''
    global edit_list
    edit_list = [0 for i in range(nx.number_of_nodes(G))]
    frozen_graph = nx.to_undirected(nx.freeze(G))
    print(nx.number_of_edges(G))
    unfrozen_graph = nx.Graph(frozen_graph)
    print(nx.number_of_edges(unfrozen_graph))
    A, A2, A3 = Adjacency(G)
    lists = read_file(G, file)
    for i in lists[num-1]:
        max = i.pop(0)
        for j in i:
            '''创建待修改列表'''
            #edit_list[int(j)-1] = nx.degree(G, max) - nx.degree(G, j)  #id从1开始
            edit_list[int(j)] = nx.degree(G,max) - nx.degree(G,j)   #id从0开始
    print(edit_list)
    process_by_id(G,unfrozen_graph,edit_list,A,A2,A3)
    nx.write_gml(unfrozen_graph,name+'.gml')
    print(nx.number_of_edges(G))
    print(len(nx.edges(unfrozen_graph)))

def process_by_id(origin_graph,unfrozen_graph,edit_list,A,A2,A3):
    '''处理一个类'''
    for i,j in zip(range(len(edit_list)),edit_list):
        if j != 0:
            addedges(i,j,unfrozen_graph,A,A2,A3)
    print('edit_lisr1:',edit_list)
    if flag == 1:
        #三跳可达矩阵无法满足，更新矩阵，最高到6跳
        A,A2,A3 = Adjacency(unfrozen_graph)
        for i, j in zip(range(len(edit_list)), edit_list):
            if j != 0:
                addedges(i, j, unfrozen_graph, A, A2, A3)
    print('edit_list2:',edit_list)
    list_add_nodes = []
    list_add_value = []
    added_list = []
    if max(edit_list) != 0:
        print('!')
        print('edit_list3:',edit_list)
        #六跳内无法满足，直接加点
        for i in edit_list:
            if i != 0:
                #需要加邻接点的节点的id
                #list_add_nodes.append(edit_list.index(i) + 1)  #id->1
                list_add_nodes.append(edit_list.index(i))   #id->0
                #防止需要加边的两个点值相同，index每次都找到第一个点
                edit_list[edit_list.index(i)] = 0
                #对应id需要加几个点
                list_add_value.append(i)
        for i in range(max(list_add_value)):
            added_list.append(str(i+1)+'-add')
            unfrozen_graph.add_node(str(i+1)+'-add')
        for i,j in zip(list_add_nodes,list_add_value):
            print(list_add_nodes)
            random.shuffle(added_list)
            for k,m in zip(range(j),added_list):
                unfrozen_graph.add_edge(i,m)
                print('add edge:',str(i),',',str(m))

def addedges(row,num,unfrozen_graph,A,A2,A3):
    '''进行加边操作'''
    global flag
    flag = 0
    while(num != 0):
        id_list = list(A2[row][:])
        id_match = id_list.index(1)
        while (edit_list[id_match] == 0):
            id_list[id_match] = 0
            if(max(id_list) == 0 and flag == 0):
                id_list = list(A3[row][:])
                flag = 1
            if(max(id_list) == 0 and flag == 1):
                break
            id_match = id_list.index(1)
        if flag == 1:
            break;
        col = int(id_match)
        #unfrozen_graph.add_edge(row + 1,col + 1)   #id->1
        unfrozen_graph.add_edge(row, col)   #id->0
        #print('add edges:',str(row+1),',',str(col+1))  #id->1
        print('add edges:', str(row), ',', str(col))    #id->0
        num -= 1
        edit_list[row] -= 1
        edit_list[col] -= 1
        A[row][col] = 1
        A[col][row] = 1
        A2[row][col] = 0
        A2[col][row] = 0
    A2[row] = 0
    A2[:,row] = 0

def adj2excel():
    A, A2, A3, A4 = Adjacency(G_kar)
    data_df = pd.DataFrame(A4)
    writer = pd.ExcelWriter('A4.xlsx')
    data_df.to_excel(writer, 'sheet1')
    writer.save()

def pict_class(G,G_anoy,file,num,dict):
    workbook = xlrd.open_workbook(file)
    mySheet1 = workbook.sheet_by_name('Sheet' + str(num))
    rows = mySheet1.nrows
    path = '/Users/mac/Desktop/networkx/' + dict
    if not os.path.exists(path):
        os.makedirs(path)
    nx.draw_networkx(G,pos=nx.circular_layout(G))
    plt.title('figure1')
    plt.savefig(path+'/'+str(nx.number_of_edges(G))+'.pdf')
    plt.close()
    nx.draw_networkx(G_anoy,pos=nx.circular_layout(G_anoy))
    plt.title('figure2')
    plt.savefig(path+'/'+str(nx.number_of_edges(G))+'+'+str(nx.number_of_edges(G_anoy)-nx.number_of_edges(G))+'.pdf')
    plt.close()
    for i in range(1,rows):
        class_list = [int(i) for i in list(mySheet1.row_values(i)) if i != '']
        for j in class_list:
            neighbor_list = list(nx.all_neighbors(G_anoy,str(j)))
            pict_list = neighbor_list[:]
            pict_list.append(str(j))
            subgraph = nx.subgraph(G_anoy,pict_list)
            nx.draw_networkx(subgraph)
            plt.title(j)
            path = '/Users/mac/Desktop/networkx/' + dict + '/' +str(i)
            if not os.path.exists(path):
                os.makedirs(path)
            plt.savefig(path + '/' + str(j) + '.pdf')
            plt.close()

if __name__ == '__main__':
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    G_1 = nx.read_gml('1.gml',label=None)
    G_HepTh = nx.read_edgelist('CA-HepTh.txt')
    G_HepTh = nx.convert_node_labels_to_integers(G_HepTh)
    G_HepPh = nx.read_edgelist('CA-HepPh.txt')
    G_HepPh = nx.convert_node_labels_to_integers(G_HepPh)
    G_kar_un = G_kar.to_undirected()
    G_1_un = G_1.to_undirected()
    #do_by_graph(G_1_un, 'com-part-com-3anoymous-1-id-3-rdivision.xlsx',4,'1-sheet4')
    #do_by_graph(G_kar_un, 'com-part-com-3anoymous-kar-3-rdivision.xlsx', 'kar-sheet4')
    '''G_kar_anoy_1 = nx.read_gml('kar-sheet1.gml')
    G_kar_anoy_2 = nx.read_gml('kar-sheet2.gml')
    G_kar_anoy_3 = nx.read_gml('kar-sheet3.gml')
    G_kar_anoy_4 = nx.read_gml('kar-sheet4.gml')
    G_kar_anoy_1 = G_kar_anoy_1.to_undirected()
    G_kar_anoy_2 = G_kar_anoy_2.to_undirected()
    G_kar_anoy_3 = G_kar_anoy_3.to_undirected()
    G_kar_anoy_4 = G_kar_anoy_4.to_undirected()
    G_1_anoy_1 = nx.read_gml('1-sheet1.gml')
    G_1_anoy_2 = nx.read_gml('1-sheet2.gml')
    G_1_anoy_3 = nx.read_gml('1-sheet3.gml')
    G_1_anoy_4 = nx.read_gml('1-sheet4.gml')
    G_1_anoy_1 = G_1_anoy_1.to_undirected()
    G_1_anoy_2 = G_1_anoy_2.to_undirected()
    G_1_anoy_3 = G_1_anoy_3.to_undirected()
    G_1_anoy_4 = G_1_anoy_4.to_undirected()'''
    #pict_class(G_1_un, G_1_anoy_1, 'com-part-com-3anoymous-1-id-3-rdivision.xlsx', 1, 'G_1_anoy_1')
    #pict_class(G_1_un,G_1_anoy_2,'com-part-com-3anoymous-1-id-3-rdivision.xlsx',2,'G_1_anoy_2')
    #pict_class(G_1_un, G_1_anoy_3, 'com-part-com-3anoymous-1-id-3-rdivision.xlsx',3, 'G_1_anoy_3')
    #pict_class(G_1_un, G_1_anoy_4, 'com-part-com-3anoymous-1-id-3-rdivision.xlsx',4,'G_1_anoy_4')
    #G_1_anoy = nx.read_gml('1-sheet1.gml')
    #G_1_anoy = G_1_anoy.to_undirected()
    #nx.draw_networkx(G_kar_un,pos=nx.circular_layout(G_kar_un))
    #nx.draw_networkx(G_1_un,pos=nx.circular_layout(G_1_un))
    #plt.show()
    #nx.draw_networkx(G_kar_anoy,pos=nx.circular_layout(G_kar_anoy))
    #nx.draw_networkx(G_1_anoy,pos=nx.circular_layout(G_1_anoy))
    #plt.show()
    #pict_class(G_kar_un, G_kar_anoy_1, 'com-part-com-3anoymous-kar-3-rdivision.xlsx', 1, 'G_kar_anoy_1')
    #pict_class(G_kar_un,G_kar_anoy_2,'com-part-com-3anoymous-kar-3-rdivision.xlsx',2,'G_kar_anoy_2')
    #pict_class(G_kar_un, G_kar_anoy_3, 'com-part-com-3anoymous-kar-3-rdivision.xlsx',3, 'G_kar_anoy_3')
    #pict_class(G_kar_un, G_kar_anoy_4, 'com-part-com-3anoymous-kar-3-rdivision.xlsx',4,'G_kar_anoy_4')
    #pict_class(G_1_anoy,'com-part-com-3anoymous-1-id-3-rdivision.xlsx','G_1_anoy')
    #G_1 = nx.to_undirected(G_1)
    #do_by_row(G_kar)
    #adj2excel()
    #print(nx.shortest_path(G_kar,2,29))

    #do_by_graph(G_1_un,'com-part-com-3anoymous-1-id-3-rdivision.xlsx','1-sheet1')
    #print(list(nx.all_neighbors(G_kar,33.0)))


