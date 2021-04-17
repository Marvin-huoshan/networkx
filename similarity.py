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
import math

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

def sim(G,file_list,name):
    list_G = list(max(nx.connected_components(G)))
    G_connect = nx.subgraph(G, list_G)
    G_connect = nx.convert_node_labels_to_integers(G_connect)
    workbook = xlsxwriter.Workbook('similarity-'+str(name)+'.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0;col = 0
    for i in tqdm(file_list,desc='ex:'):
        print(i)
        G_modify = nx.read_gml(i)
        worksheet.write(2 * row,col,name)
        col += 1
        print('G_connect edges:',nx.number_of_edges(G_connect))
        print('G_modify edges:',nx.number_of_edges(G_modify))
        ME = nx.number_of_edges(G_modify) - nx.number_of_edges(G_connect)
        print('边改变量：',ME)
        worksheet.write(2 * row,col,ME)
        worksheet.write(2 * row + 1,col,ME / nx.number_of_edges(G_connect))
        col += 1
        print('G_connect AVE:', 2 * nx.number_of_edges(G_connect) / nx.number_of_nodes(G_connect))
        print('G_modify AVE:', 2 * nx.number_of_edges(G_modify) / nx.number_of_nodes(G_modify))
        print('平均度改变量：', 2 * nx.number_of_edges(G_modify) / nx.number_of_nodes(G_modify) - 2 * nx.number_of_edges(G_connect) / nx.number_of_nodes(G_connect))
        AVE = 2 * nx.number_of_edges(G_modify) / nx.number_of_nodes(G_modify) - 2 * nx.number_of_edges(G_connect) / nx.number_of_nodes(G_connect)
        worksheet.write(2 * row,col,AVE)
        worksheet.write(2 * row + 1,col,AVE / (2 * nx.number_of_edges(G_connect) / nx.number_of_nodes(G_connect)))
        col += 1
        print('G_connect ACC:', avg_cluster(G_connect))
        print('G_modify ACC:', avg_cluster(G_modify))
        print('平均聚类系数改变量：', avg_cluster(G_modify) - avg_cluster(G_connect))
        ACC = avg_cluster(G_modify) - avg_cluster(G_connect)
        worksheet.write(2 * row,col,ACC)
        worksheet.write(2 * row + 1,col,ACC / avg_cluster(G_connect))
        col += 1
        print('G_connect APL:', avg_shortest_path(G_connect))
        print('G_modify APL:', avg_shortest_path(G_modify))
        print('平均最短路径改变量：', avg_shortest_path(G_modify) - avg_shortest_path(G_connect))
        APL = avg_shortest_path(G_modify) - avg_shortest_path(G_connect)
        worksheet.write(2 * row,col,APL)
        worksheet.write(2 * row + 1,col,APL / avg_shortest_path(G_connect))
        col += 1
        sum1 = 0
        sum2 = 0
        dict1 = nx.betweenness_centrality(G_connect)
        dict2 = nx.betweenness_centrality(G_modify)
        for val1 in dict1.values():
            sum1 += val1
        for val2 in dict2.values():
            sum2 += val2
        print('G_connect ABC:', sum1 / nx.number_of_nodes(G_connect))
        print('G_modify ABC:', sum2 / nx.number_of_nodes(G_modify))
        print('平均中心性改变量：', sum2 / nx.number_of_nodes(G_modify) - sum1 / nx.number_of_nodes(G_connect))
        ABC = sum2 / nx.number_of_nodes(G_modify) - sum1 / nx.number_of_nodes(G_connect)
        worksheet.write(2 * row,col,ABC)
        worksheet.write(2 * row + 1,col,ABC / (sum1 / nx.number_of_nodes(G_connect)))
        row += 1
        col = 0
    workbook.close()

def subgraph_sim(G,G_origin,file):
    workbook = xlrd.open_workbook(file)
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    workbook = xlsxwriter.Workbook('HepTH_5_2.xlsx')
    worksheet = workbook.add_worksheet()
    list1 = []
    nrows = mySheet2.nrows
    for i in tqdm(range(1,nrows)):
        tmp_list1 = [i for i in list(mySheet2.row_values(i)) if i != '']
        tmp_list1 = sorted(tmp_list1, key=lambda x: nx.degree(G, x), reverse=True)
        list1.append(tmp_list1)
    for i in tqdm(range(len(list1))):
        subgraph_sim_1(G,G_origin,list1[i],i,worksheet)
    workbook.close()

def subgraph_sim_1(G,G_origin,list_class,row,worksheet):
    worksheet.write(3*row, 0, '类' + str(row))
    worksheet.write(3*row + 1, 0, '原IGF')
    worksheet.write(3*row + 2, 0, '修改后IGF')
    for i in range(len(list_class)):
        IGF1 = compute_IGF(G,list_class[i])
        IGF2 = compute_IGF(G_origin,list_class[i])
        worksheet.write(3*row,i+1,list_class[i])
        worksheet.write(3*row+1,i+1,IGF1)
        worksheet.write(3*row + 2, i + 1, IGF2)


def compute_IGF(G,node):
    sublist = list(nx.all_neighbors(G,node))
    sublist.append(node)
    subgraph = G.subgraph(sublist)
    print(nx.number_of_edges(subgraph))
    item1 = 0
    for i in nx.nodes(G):
        item1 += (nx.degree(G,i) * math.log(nx.degree(G,i)))
    IGF = math.log(2 * nx.number_of_edges(subgraph)) - (1/(2 * nx.number_of_edges(subgraph))) * item1
    return IGF

def indexs(G,name):
    '''计算每个节点的IGF，中心性，聚类系数'''
    #首先将图中节点按照度从大到小排序
    node_list = list(nx.nodes(G))
    node_list = sorted(node_list, key=lambda x: nx.degree(G, x), reverse=True)
    workbook = xlsxwriter.Workbook(name+'.xlsx')
    worksheet = workbook.add_worksheet()
    print(nx.betweenness_centrality(G))
    dict_betweeness = nx.betweenness_centrality(G)
    worksheet.write(0,0,'节点')
    worksheet.write(0,1,'IGF')
    worksheet.write(0,2,'BC')
    worksheet.write(0,3,'LC')
    for i in tqdm(range(len(node_list))):
        IGF = compute_IGF(G,node_list[i])
        #介数中心性
        BC = dict_betweeness[i]
        #聚类系数
        LC = nx.clustering(G,i)
        worksheet.write(i,0,node_list[i])
        worksheet.write(i,1,IGF)
        worksheet.write(i,2,BC)
        worksheet.write(i,3,LC)
    workbook.close()
import matplotlib
from matplotlib import pyplot as plt
import math

def degree_dis_plot(G,file_list):
    '''
    画出度分布图
    :param G:
    :param file_list:
    :return:
    '''
    G_modify_5 = nx.read_gml(file_list[0])
    G_modify_10 = nx.read_gml(file_list[1])
    G_modify_15 = nx.read_gml(file_list[2])
    G_modify_20 = nx.read_gml(file_list[3])
    G_modify_25 = nx.read_gml(file_list[4])
    num = nx.number_of_nodes(G)
    dicts_1 = dict(get_degree_count(G,num))
    dicts_5 = dict(get_degree_count(G_modify_5,num))
    dicts_10 = dict(get_degree_count(G_modify_10,num))
    dicts_15 = dict(get_degree_count(G_modify_15,num))
    dicts_20 = dict(get_degree_count(G_modify_20,num))
    dicts_25 = dict(get_degree_count(G_modify_25,num))
    x_1 = list(dicts_1.keys())
    y_1 = list(dicts_1.values())
    x_5 = list(dicts_5.keys())
    y_5 = list(dicts_5.values())
    x_10 = list(dicts_10.keys())
    y_10 = list(dicts_10.values())
    x_15 = list(dicts_15.keys())
    y_15 = list(dicts_15.values())
    x_20 = list(dicts_20.keys())
    y_20 = list(dicts_20.values())
    x_25 = list(dicts_25.keys())
    y_25 = list(dicts_25.values())
    x = [5,10,15,20,25]
    face_y = [5050.403562,7854.694487,17863.40825,22886.27994,33115.55346,17719.63467]
    HepTh_y = [751.9714487,914.5636706,992.1375961,1339.006074,1488.205347,2123.542722]
    Email_y = [9740.64618,7592.988059,25536.55068,36852.44825,33729.62218,29528.95649]
    matplotlib.rc('figure', figsize=(8, 8))
    plt.plot(x_25, y_25, color='c', linestyle='-', marker='D',label='k=25')
    plt.plot(x_20, y_20, color='y', linestyle='-', marker='x',label='k=20')
    plt.plot(x_15, y_15, color='g', linestyle='-', marker='s',label='k=15')
    plt.plot(x_10, y_10, color='b', linestyle='-', marker='v',label='k=10')
    plt.plot(x_5, y_5, color='r', linestyle='-', marker='*',label='k=5')
    plt.plot(x_1, y_1, color='k', linestyle='-', marker='.',label='Origin')
    plt.xlabel('Degree')
    plt.ylabel('log(n)')
    plt.legend()
    plt.ylim(0,4)
    #plt.yticks(my_y_ticks)
    plt.show()

def get_degree_count(G,num):
    '''
    获得每个图的度值以及其对应个数
    :return:
    '''
    degree = sorted(list(dict(nx.degree(G)).values())[:num], reverse=False)
    print(degree)
    degree_value = sorted(list(set(degree)))
    degree_count = list()
    for i in degree_value:
        degree_count.append(math.log10(degree.count(i)))
    x = degree_value
    y = degree_count
    return zip(x,y)

def short_path_without_addnodes(G,file_list):
    for i in file_list:
        G_mod = nx.read_gml(i)
        list1 = nx.nodes(G)
        length = len(list1)
        list2 = list(nx.nodes(G_mod))[:length]
        G_sub_mod = nx.subgraph(G_mod,list2)
        print(i,':',avg_shortest_path(G_sub_mod))


if __name__ == '__main__':
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    G_1 = nx.read_gml('1.gml', label=None)
    G_HepTh = nx.read_edgelist('CA-HepTh.txt')
    G_Email = nx.read_edgelist('Email-Enron.txt')
    G_face = nx.read_edgelist('facebook_combined.txt')
    G_cond = nx.read_edgelist('CA-CondMat.txt')
    list_HepTh = list(max(nx.connected_components(G_HepTh)))
    list_face = list(max(nx.connected_components(G_face)))
    list_Email = list(max(nx.connected_components(G_Email)))
    list_cond = list(max(nx.connected_components(G_cond)))
    G_HepTh_connect = nx.subgraph(G_HepTh, list_HepTh)
    G_face_conect = nx.subgraph(G_face,list_face)
    G_Email_connect = nx.subgraph(G_Email,list_Email)
    G_cond_connect = nx.subgraph(G_cond,list_cond)
    G_HepTh_connect = nx.convert_node_labels_to_integers(G_HepTh_connect)
    G_face_conect = nx.convert_node_labels_to_integers(G_face_conect)
    G_Email_connect = nx.convert_node_labels_to_integers(G_Email_connect)
    G_cond_connect = nx.convert_node_labels_to_integers(G_cond_connect)
    G_HepPh = nx.read_edgelist('CA-HepPh.txt')
    G_HepPh = nx.convert_node_labels_to_integers(G_HepPh)
    G_kar_un = G_kar.to_undirected()
    G_1_un = G_1.to_undirected()
    G_connect = G_HepTh_connect

    #G_1_anoy_1 = nx.read_gml('1-sheet1.gml')
    #G_1_anoy_2 = nx.read_gml('1-sheet2.gml')
    #G_1_anoy_3 = nx.read_gml('1-sheet3.gml')
    #G_1_anoy_4 = nx.read_gml('1-sheet4.gml')
    #G_kar_anoy_1 = nx.read_gml('kar-sheet1.gml')
    #G_kar_anoy_2 = nx.read_gml('kar-sheet2.gml')
    #G_kar_anoy_3 = nx.read_gml('kar-sheet3.gml')
    #G_kar_anoy_4 = nx.read_gml('kar-sheet4.gml')
    HepTh_list = ['HepTh-nect-conv-5-sheet2.gml',
                  'HepTh-nect-conv-10-sheet2.gml',
                  'HepTh-nect-conv-15-sheet2.gml',
                  'HepTh-nect-conv-20-sheet2.gml',
                  'HepTh-nect-conv-25-sheet2.gml'
                  ]
    short_path_without_addnodes(G_HepTh_connect,HepTh_list)
    face_list = ['face-nect-conv-5-sheet2.gml',
                  'face-nect-conv-10-sheet2.gml',
                  'face-nect-conv-15-sheet2.gml',
                 'face-nect-conv-20-sheet2.gml',
                 'face-nect-conv-25-sheet2.gml'
                 ]
    Email_list = ['Email-nect-conv-5-sheet2.gml',
                  'Email-nect-conv-10-sheet2.gml',
                  'Email-nect-conv-15-sheet2.gml',
                  'Email-nect-conv-20-sheet2.gml',
                  'Email-nect-conv-25-sheet2.gml'
                  ]
    cond_list = ['conda-nect-conv-5-sheet2.gml',
                 'conda-nect-conv-10-sheet2.gml',
                 'conda-nect-conv-15-sheet2.gml',
                 'conda-nect-conv-20-sheet2.gml',
                 'conda-nect-conv-25-sheet2.gml'
                 ]
    test_list = [
        'face-nect-conv-5-sheet2.gml', 'face-nect-conv-5-sheet3.gml','face-nect-conv-5-sheet4.gml'
    ]
    #degree_dis_plot(G_cond_connect,cond_list)

    '''x = [5, 10, 15, 20, 25, 30]
    face_y = [5050.403562, 7854.694487, 17863.40825, 22886.27994, 33115.55346, 17719.63467]
    face_y = [math.log10(i) for i in face_y]
    HepTh_y = [751.9714487, 914.5636706, 992.1375961, 1339.006074, 1488.205347, 2123.542722]
    HepTh_y = [math.log10(i) for i in HepTh_y]
    Email_y = [9740.64618, 7592.988059, 25536.55068, 36852.44825, 33729.62218, 29528.95649]
    Email_y = [math.log10(i) for i in Email_y]
    matplotlib.rc('figure', figsize=(8, 8))
    plt.plot(x, face_y, color='b', linestyle='-', marker='v', label='Facebook')
    plt.plot(x, HepTh_y, color='r', linestyle='-', marker='*', label='ca-HepTh')
    plt.plot(x, Email_y, color='g', linestyle='-', marker='s', label='Enron')
    plt.xlabel('k')
    plt.ylabel('log(n)')
    plt.legend()
    plt.ylim(2.5,5)
    # plt.yticks(my_y_ticks)
    plt.show()'''
    #G_HepTh_5anoy2 = nx.read_gml('HepTh-nect-5-sheet2.gml')
    #G_HepTh_5anoy2 = nx.convert_node_labels_to_integers(G_HepTh_5anoy2)
    #indexs(G_HepTh_connect,'HepTh_connect_index')
    #subgraph_sim(G_HepTh_5anoy2,G_HepTh_connect,'com-part-com-5anoymous-HepTh-id-connect-3-rdivision.xlsx')
    #sim(G_face,test_list,'test_conv')
    #print(nx.number_of_nodes())
    #sim(G_Email,Email_list,'G_Email_conv')

    '''print(2*nx.number_of_edges(G_kar)/nx.number_of_nodes(G_kar))
    print(2*nx.number_of_edges(G_kar_anoy_1)/nx.number_of_nodes(G_kar_anoy_1))
    print(2 * nx.number_of_edges(G_1) / nx.number_of_nodes(G_1))
    print(2 * nx.number_of_edges(G_1_anoy_1) / nx.number_of_nodes(G_1_anoy_1))
    print('{:.2%}'.format((avg_cluster(G_1)-avg_cluster(G_1_anoy_1))/avg_cluster(G_1)))
    print('{:.2%}'.format((avg_shortest_path(G_1) - avg_shortest_path(G_1_anoy_1)) / avg_shortest_path(G_1)))
    print('{:.2%}'.format(avg_betweenness_change(G_1,G_1_anoy_1)))
    print(avg_cluster(G_1))
    print(avg_cluster(G_1_anoy_1))
    print(avg_shortest_path(G_1))
    print(avg_shortest_path(G_1_anoy_1))'''