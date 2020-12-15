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

def multi_process(G,file,name):
    '''使用多进程'''

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
    for i in range(1,mySheet1.nrows):
        tmp_list1 = [i for i in list(mySheet1.row_values(i)) if i != '']
        list1.append(tmp_list1)
        tmp_list2 = [i for i in list(mySheet2.row_values(i)) if i != '']
        list2.append(tmp_list2)
        tmp_list3 = [i for i in list(mySheet3.row_values(i)) if i != '']
        list3.append(tmp_list3)
        tmp_list4 = [i for i in list(mySheet4.row_values(i)) if i != '']
        list4.append(tmp_list4)
    lists.append(list1)
    lists.append(list2)
    lists.append(list3)
    lists.append(list4)
    read_class(G, lists[0],name+'-sheet1')
    #read_class(G, lists[1],name+'-sheet2')
    #read_class(G, lists[2],name+'-sheet3')
    #read_class(G, lists[3],name+'-sheet4')

def read_class(G,list1,name):
    '''从划分好的类中取节点，将同一类中小度节点图转化为大度图'''
    frozen_graph = nx.freeze(G)
    manager = BaseManager()
    manager.register('Graph', Graph)
    manager.start()
    unfrozen_graph = manager.Graph(G)
    list1.reverse()
    p = Pool(processes=42)
    for i in tqdm(range(len(list1)),desc='逐行进行图修改'):
        p.apply_async(process_by_row,args=(G,unfrozen_graph,list1[i],i,))
    p.close()
    p.join()
    nx.write_edgelist(unfrozen_graph,name+'.edglist')

def process_by_row(original_graph,unfrozen_graph,list1,row):
    '''处理同一类的一行数据'''
    #🤓
    max = find_max_graph(unfrozen_graph, list1)  # 找出每一个类最大的那个子图
    #list_max = list(nx.all_neighbors(unfrozen_graph,max))
    #list_max.append(max)
    #subgraph_max = nx.subgraph(unfrozen_graph,list_max)
    #print('max:',nx.number_of_edges(subgraph_max))
    for i in tqdm(list1, desc=str(row) + '行进度'):
        if find_OEP_with(original_graph,i,max) != -1:
            list_edit = find_OEP_with(original_graph, i, max)
            max_node_map = np.array(list_edit[len(list_edit)-1][0])
            #max_origin = map_list(max,max_node_map)
        else:
            continue
        g_modify(unfrozen_graph, list_edit,row)

def map_list(max,list1):
    print('map')
    print(list1)
    for i in range(len(list1)):
        if list1[i][1] == max:
            return list1[i][0]



def find_OEP_with(G,node1,node2):
    '''将node1所代表的一邻居图转化为node2所代表的一邻居图'''
    list1 = list(nx.all_neighbors(G,node1))
    list2 = list(nx.all_neighbors(G,node2))
    list1.append(node1)
    list2.append(node2)
    #创建节点的一邻居子图（包含自己）
    subgraph1 = nx.subgraph(G,list1)
    subgraph2 = nx.subgraph(G,list2)
    number1 = nx.number_of_edges(subgraph1)
    number2 = nx.number_of_edges(subgraph2)
    if abs(number1-number2) == 1:
        return -1
    elif (abs(number2-number1)/max(number1,number2)) > 0.1:
        return list(nx.optimize_edit_paths(subgraph1,subgraph2,timeout=18000))
    else:
        return -1

def g_modify(G,list1,row):
    '''按照图修改列表进行图修改'''
    modify_list = list1[:]
    length = len(modify_list) - 1
    node_map = np.array(modify_list[length][0])
    edge_map = np.array(modify_list[length][1],dtype=object)
    cost = modify_list[length][2]
    for i in node_map:
        if i[0] == None:
            '''加点操作'''
            if isinstance(i[1],str):
                G.add_node(i[1]+'-add-in'+str(row))
            else:
                G.add_node(-i[1])
    for i in edge_map:
        if None in i:
            '''将带None的修改边的对，以及节点的映射关系传入函数，进行边的操作'''
            edit_edges(G,i,node_map,row)


def edit_edges(G,edge_list,node_map,row):
    '''根据传来的边修改列表，进行边修改操作'''
    remove_list = []
    add_list = []
    tmp = list(edge_list)
    if tmp.index(None) == 0:    #加边操作
        tmp.remove(None)
        add_list.append(tmp.pop())
        Gadd_list(G,add_list,node_map,row)
    else:   #减边操作
        tmp.remove(None)
        remove_list.append(tmp.pop())
        Gremove_list(G,remove_list)

def Gremove_list(G,remove_list):
    '''原图中删除原来存在的边'''
    G.remove_edges_from(remove_list)

def Gadd_list(G,add_list,node_map,row):
    '''原图中增加新的边'''
    tmp_list = []
    new_add_list = []
    for i in range(len(add_list)):
        for j in range(2):
            tmp_list.append(str(Gnode_map(add_list[i][j],node_map,row)))
    new_add_list.append(tuple(tmp_list))
    G.add_edges_from(new_add_list)

def Gnode_map(num,node_map,row):
    '''根据映射列表，将点映射回原图'''
    for i in range(len(node_map)):
        if node_map[i][1] == num and node_map[i][0] != None:
            return node_map[i][0]
        elif isinstance(num,str):
            return num+'-add-in'+str(row)
        else:
            return -num


def test(G,node):
    G.add_node(node)
    print(nx.nodes(G))

def node_edit(G,list1):
    '''根据传入的列表，构造整个图中节点的修改数组'''
    length = len(list1) - 1

def draw_subgraph(node1,node2,G1,G2):
    list1 = list(nx.all_neighbors(G1, node1))
    list1.append(node1)
    subgraph1 = nx.subgraph(G1, list1)
    nx.draw_networkx(subgraph1)
    print('G_1:',nx.number_of_edges(subgraph1))
    plt.show()
    list3 = list(nx.all_neighbors(G2, node1))
    list3.append(node1)
    subgraph3 = nx.subgraph(G2, list3)
    nx.draw_networkx(subgraph3)
    print('G_1_1:',nx.number_of_edges(subgraph3))
    plt.show()
    list2 = list(nx.all_neighbors(G1, node2))
    list2.append(node2)
    subgraph2 = nx.subgraph(G1, list2)
    nx.draw_networkx(subgraph2)
    print('G_1:',nx.number_of_edges(subgraph2))
    plt.show()
    list4 = list(nx.all_neighbors(G2, node2))
    list4.append(node2)
    subgraph4 = nx.subgraph(G2, list4)
    nx.draw_networkx(subgraph4)
    print('G_1_1:',nx.number_of_edges(subgraph4))
    plt.show()

def test_frozen(name1,name2,name3,G1,G2,G3):
    print(name1+' number of edges:',nx.number_of_edges(G1))
    print(name2+' number of edges:',nx.number_of_edges(G2))
    print(name3+' number of edges:',nx.number_of_edges(G3))
    print(name1+' number of nodes:',nx.number_of_nodes(G1))
    print(name2+' number of nodes:',nx.number_of_nodes(G2))
    print(name3+' number of nodes:',nx.number_of_nodes(G3))
    plt.figure(figsize=(18, 8))
    nx.draw_networkx(G1,pos=nx.circular_layout(G1))
    plt.show()
    plt.figure(figsize=(18, 8))
    nx.draw_networkx(G2, pos=nx.circular_layout(G2))
    plt.show()
    plt.figure(figsize=(18, 8))
    nx.draw_networkx(G3, pos=nx.circular_layout(G3))
    plt.show()

if __name__ == '__main__':
    G_1 = nx.read_gml('1-copy-1.gml')
    G_1 = nx.to_undirected(G_1)
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    #multi_process(G_1,'com-part-com-3anoymous-1-3-rdivision.xlsx','1')
    G_kar_OED = nx.read_edgelist('kar-18-sheet1.edglist')
    G_kar_OED_unfrozen = nx.read_edgelist('kar-unfrozen-18-sheet1.edglist')
    test_frozen('G_kar','G_kar_OED','G_kar_OED_unfrozen',G_kar,G_kar_OED,G_kar_OED_unfrozen)
    G_1_OED = nx.read_edgelist('1-passlittle-sheet1.edglist')
    G_1_unfrozen = nx.read_edgelist('1-unfrozen-passlittle-sheet1.edglist')
    test_frozen('G_1','G_1_OED','G_1_unfrozen',G_1,G_1_OED,G_1_unfrozen)
    #frozen_graph = nx.freeze(G_1)
    #unfrozen_graph = nx.Graph(frozen_graph)
    #list1 = list(find_OEP_with(G_1,'11','86'))
    #print(list1[len(list1)-1])
    #g_modify(unfrozen_graph,list1,'19')

    #G_1_1 = nx.read_edgelist('1-sheet1.edglist')
    #G_1_2 = nx.read_edgelist('1-1-sheet1.edglist')
    #G_1_1 = nx.read_edgelist('1-sheet1.edglist')

    #print('=========')
    #draw_subgraph('11','35',G_1,G_1_2)
    '''frozen_graph = nx.freeze(G_1)
    unfrozen_graph = nx.Graph(frozen_graph)
    manager = BaseManager()
    manager.register('Graph',nx.Graph)
    manager.start()
    unfrozen_graph = manager.Graph(frozen_graph)
    p = Pool(3)
    for i in range(3):
        it = p.apply_async(test,args=(unfrozen_graph,str(i)+'s',)).get()
        print(it)
    p.close()
    p.join()
    print(nx.nodes(unfrozen_graph))'''

    #p.apply_async(multi_process,args=(('com-part-com-3anoymous-1-3-rdivision.xlsx','1-3-3')))
    #p.apply_async(multi_process,args=(('com-part-com-4anoymous-1-3-rdivision.xlsx','1-4-3')))
    #p.apply_async(multi_process,args=(('com-part-com-3anoymous-kar-3-rdivision.xlsx','kar-3-3')))
    #p.close()
    #p.join()
    #frozen_graph = nx.freeze(G)

    #print(nx.nodes(G_1_1))
    '''list1 = list(nx.all_neighbors(G_1_1, '218'))
    list3 = list(nx.all_neighbors(G_1,'218'))
    list1.append('218')
    subgraph1 = nx.subgraph(G_1_1, list1)
    nx.draw_networkx(subgraph1)
    print(nx.number_of_edges(subgraph1))
    plt.show()
    list2 = list(nx.all_neighbors(G_1_1, '117'))
    list2.append('117')
    subgraph2 = nx.subgraph(G_1_1,list2)
    nx.draw_networkx(subgraph2)
    print(nx.number_of_edges(subgraph2))
    plt.show()'''
    '''list1 = list(nx.all_neighbors(G_1,'130'))
    list1.append('130')
    #print(list1)
    subgraph1 = nx.subgraph(G_1,list1)
    list2 = list(nx.all_neighbors(G_1,'134'))
    list2.append('134')
    #print(list2)
    subgraph2 = nx.subgraph(G_1,list2)
    list3 = list(nx.optimize_edit_paths(subgraph1,subgraph2))
    print(list3)
    length = len(list3) - 1
    print(length)
    print(list3[length])
    for i in list3[length]:
        print(i)
    #plt1 = nx.draw_networkx(subgraph1)
    #plt.show()
    #plt2 = nx.draw_networkx(subgraph2)
    #plt.show()
    array1 = np.array(list3[length][0])
    print(array1)
    print(array1[0][0])
    array2 = np.array(list3[length][1],dtype=object)
    print(array2)
    tmp_list = []
    for i in array2:
        if None in i:
            tmp = list(i)
            tmp.remove(None)
            tmp_list.append(tmp.pop())
    print(tmp_list)
    for i in range(len(tmp_list)):
        for j in range(2):
            print(tmp_list[i][j])
    #print(nx.number_of_edges(subgraph2))'''

    #！！！
    '''list1 = [i for i in list(mySheet.row_values(i)) if i != '']
            max = find_max_graph(G,list1)   #找出每一个类最大的那个子图
            list_max = list(nx.all_neighbors(G,max))
            list_max.append(max)
            subgraph_max = nx.subgraph(G,list_max)
            print('max i:' + max)
            print('max edges:',nx.number_of_edges(subgraph_max))
            nx.draw_networkx(subgraph_max)
            plt.title('max:' + max)
            plt.savefig(path + 'max-' + str(max) + '.png')
            plt.close()
            list1.remove(max)
            for i in tqdm(list1,desc='当前行进度'):
                list1 = find_OEP_with(unfrozen_graph,i,max)
                list_before = list(nx.all_neighbors(G,i))
                list_before.append(i)
                subgraph_before = nx.subgraph(G,list_before)
                nx.draw_networkx(subgraph_before)
                print('before i:' + i)
                print('before edges:',nx.number_of_edges(subgraph_before))
                #plt.savefig(path + 'before-' + str(i) + '.png')
                plt.close()
                g_modify(unfrozen_graph,list1)
                list_after = list(nx.all_neighbors(unfrozen_graph, i))
                list_after.append(i)
                subgraph_after = nx.subgraph(unfrozen_graph, list_after)
                nx.draw_networkx(subgraph_after)
                print('after edges:',nx.number_of_edges(subgraph_after))
                #plt.savefig(path + 'after-' + str(i) + '.png')
                print(list1[len(list1)-1][0])
                print(list1[len(list1)-1][1])
                plt.close()'''
