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


if __name__ == '__main__':
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    G_1 = nx.read_gml('1.gml', label=None)
    G_HepTh = nx.read_edgelist('CA-HepTh.txt')
    G_Email = nx.read_edgelist('Email-Enron.txt')
    G_face = nx.read_edgelist('facebook_combined.txt')
    list_HepTh = list(max(nx.connected_components(G_HepTh)))
    G_HepTh_connect = nx.subgraph(G_HepTh, list_HepTh)
    G_HepTh_connect = nx.convert_node_labels_to_integers(G_HepTh_connect)
    G_HepPh = nx.read_edgelist('CA-HepPh.txt')
    G_HepPh = nx.convert_node_labels_to_integers(G_HepPh)
    G_kar_un = G_kar.to_undirected()
    G_1_un = G_1.to_undirected()
    #G_1_anoy_1 = nx.read_gml('1-sheet1.gml')
    #G_1_anoy_2 = nx.read_gml('1-sheet2.gml')
    #G_1_anoy_3 = nx.read_gml('1-sheet3.gml')
    #G_1_anoy_4 = nx.read_gml('1-sheet4.gml')
    #G_kar_anoy_1 = nx.read_gml('kar-sheet1.gml')
    #G_kar_anoy_2 = nx.read_gml('kar-sheet2.gml')
    #G_kar_anoy_3 = nx.read_gml('kar-sheet3.gml')
    #G_kar_anoy_4 = nx.read_gml('kar-sheet4.gml')
    HepTh_list = ['HepTh-nect-conv-5-sheet2.gml','HepTh-nect-conv-5-sheet3.gml','HepTh-nect-conv-5-sheet4.gml',
                  'HepTh-nect-conv-10-sheet2.gml','HepTh-nect-conv-10-sheet3.gml','HepTh-nect-conv-10-sheet4.gml',
                  'HepTh-nect-conv-15-sheet2.gml','HepTh-nect-conv-15-sheet3.gml','HepTh-nect-conv-15-sheet4.gml',
                  'HepTh-nect-conv-20-sheet2.gml', 'HepTh-nect-conv-20-sheet3.gml', 'HepTh-nect-conv-20-sheet4.gml',
                  'HepTh-nect-conv-25-sheet2.gml', 'HepTh-nect-conv-25-sheet3.gml', 'HepTh-nect-conv-25-sheet4.gml',
                  'HepTh-nect-conv-30-sheet2.gml', 'HepTh-nect-conv-30-sheet3.gml', 'HepTh-nect-conv-30-sheet4.gml'
                  ]
    face_list = ['face-nect-conv-5-sheet2.gml','face-nect-conv-5-sheet3.gml','face-nect-conv-5-sheet4.gml',
                  'face-nect-conv-10-sheet2.gml','face-nect-conv-10-sheet3.gml','face-nect-conv-10-sheet4.gml',
                  'face-nect-conv-15-sheet2.gml','face-nect-conv-15-sheet3.gml','face-nect-conv-15-sheet4.gml',
                 'face-nect-conv-20-sheet2.gml', 'face-nect-conv-20-sheet3.gml', 'face-nect-conv-20-sheet4.gml',
                 'face-nect-conv-25-sheet2.gml', 'face-nect-conv-25-sheet3.gml', 'face-nect-conv-25-sheet4.gml',
                 'face-nect-conv-30-sheet2.gml', 'face-nect-conv-30-sheet3.gml', 'face-nect-conv-30-sheet4.gml'
                 ]
    Email_list = ['Email-nect-conv-5-sheet2.gml','Email-nect-conv-5-sheet3.gml','Email-nect-conv-5-sheet4.gml',
                  'Email-nect-conv-10-sheet2.gml','Email-nect-conv-10-sheet3.gml','Email-nect-conv-10-sheet4.gml',
                  'Email-nect-conv-15-sheet2.gml','Email-nect-conv-15-sheet3.gml','Email-nect-conv-15-sheet4.gml',
                  'Email-nect-conv-20-sheet2.gml', 'Email-nect-conv-20-sheet3.gml', 'Email-nect-conv-20-sheet4.gml',
                  'Email-nect-conv-25-sheet2.gml', 'Email-nect-conv-25-sheet3.gml', 'Email-nect-conv-25-sheet4.gml',
                  'Email-nect-conv-30-sheet2.gml', 'Email-nect-conv-30-sheet3.gml', 'Email-nect-conv-30-sheet4.gml'
                  ]
    test_list = [
        'face-nect-conv-5-sheet2.gml', 'face-nect-conv-5-sheet3.gml','face-nect-conv-5-sheet4.gml'
    ]
    #G_HepTh_5anoy2 = nx.read_gml('HepTh-nect-5-sheet2.gml')
    #G_HepTh_5anoy2 = nx.convert_node_labels_to_integers(G_HepTh_5anoy2)
    #indexs(G_HepTh_connect,'HepTh_connect_index')
    #subgraph_sim(G_HepTh_5anoy2,G_HepTh_connect,'com-part-com-5anoymous-HepTh-id-connect-3-rdivision.xlsx')
    sim(G_face,test_list,'test_conv')
    #sim(G_HepTh,HepTh_list,'G_HepTh_conv')
    #sim(G_Email,Email_list,'G_Email_conv')
    #sim(G_face,face_list,'G_face_conv')
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