import networkx as nx
import matplotlib.pyplot as plt
import xlsxwriter
import xlrd
import numpy as np
import time
from tqdm import tqdm
from multiprocessing import Pool,Process

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
    p = Pool(4)
    workbook = xlrd.open_workbook(file)
    mySheet1 = workbook.sheet_by_name('Sheet1')
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    p.apply_async(read_class, args=(G, mySheet1,name+'-sheet1'))
    p.apply_async(read_class, args=(G, mySheet2,name+'-sheet2'))
    p.apply_async(read_class, args=(G, mySheet3,name+'-sheet3'))
    p.apply_async(read_class, args=(G, mySheet4,name+'-sheet4'))
    p.close()
    p.join()

def read_class(G,mySheet,name):
    '''从划分好的类中取节点，将同一类中小度节点图转化为大度图'''
    #path = '/Users/mac/Desktop/g_modify/'
    frozen_graph = nx.freeze(G)
    unfrozen_graph = nx.Graph(frozen_graph)

    nrows = mySheet.nrows
    p = Pool(10)
    for i in tqdm(range(64,nrows),desc='逐行进行图修改'):
        p.apply_async(process_by_row,args=(frozen_graph,mySheet,i))
    nx.write_gml(unfrozen_graph, name + '.gml')
    p.close()
    p.join()


def process_by_row(G,mySheet,i):
    '''处理同一类的一行数据'''
    #🤓
    list1 = [i for i in list(mySheet.row_values(i)) if i != '']
    max = find_max_graph(G, list1)  # 找出每一个类最大的那个子图
    list1.remove(max)
    for i in tqdm(list1, desc='当前行进度'):
        if find_OEP_with(G,i,max) != -1:
            list_edit = find_OEP_with(G, i, max)
        else:
            continue
        g_modify(G, list_edit)

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
    if (abs(number2-number1)/max(number1,number2)) > 0.1:
        return list(nx.optimize_edit_paths(subgraph1,subgraph2,timeout=3600))
    else:
        return -1

def g_modify(G,list1):
    '''按照图修改列表进行图修改'''
    modify_list = list1[:]
    length = len(modify_list) - 1
    node_map = np.array(modify_list[length][0])
    edge_map = np.array(modify_list[length][1],dtype=object)
    cost = modify_list[length][2]
    for i in node_map:
        if i[0] == None:
            '''加点操作'''
            G.add_node(i[1]+'-add')
    for i in edge_map:
        if None in i:
            '''将带None的修改边的对，以及节点的映射关系传入函数，进行边的操作'''
            edit_edges(G,i,node_map)


def edit_edges(G,edge_list,node_map):
    '''根据传来的边修改列表，进行边修改操作'''
    remove_list = []
    add_list = []
    #for i in edge_list:
    tmp = list(edge_list)
    if tmp.index(None) == 0:    #加边操作
        tmp.remove(None)
        add_list.append(tmp.pop())
        Gadd_list(G,add_list,node_map)
    else:   #减边操作
        tmp.remove(None)
        remove_list.append(tmp.pop())
        Gremove_list(G,remove_list)

def Gremove_list(G,remove_list):
    '''原图中删除原来存在的边'''
    G.remove_edges_from(remove_list)

def Gadd_list(G,add_list,node_map):
    '''原图中增加新的边'''
    tmp_list = []
    new_add_list = []
    for i in range(len(add_list)):
        for j in range(2):
            tmp_list.append(str(Gnode_map(add_list[i][j],node_map)))
    new_add_list.append(tuple(tmp_list))
    G.add_edges_from(new_add_list)

def Gnode_map(num,node_map):
    '''根据映射列表，将点映射回原图'''
    for i in range(len(node_map)):
        if node_map[i][1] == num and node_map[i][0] != None:
            return node_map[i][0]
    return num+'-add'




def node_edit(G,list1):
    '''根据传入的列表，构造整个图中节点的修改数组'''
    length = len(list1) - 1

if __name__ == '__main__':
    t0 = time.perf_counter()
    G_1 = nx.read_gml('1-copy-1.gml')
    G_1 = nx.to_undirected(G_1)
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    read_class(G_1,'com-part-com-3anoymous-1-3-rdivision.xlsx','1')
    '''G_1_1 = nx.read_gml('1-1.gml')
    list1 = list(nx.all_neighbors(G_1_1, '210'))
    list1.append('210')
    subgraph1 = nx.subgraph(G_1_1, list1)
    nx.draw_networkx(subgraph1)
    plt.show()
    list2 = list(nx.all_neighbors(G_1, '65'))
    list2.append('65')
    subgraph2 = nx.subgraph(G_1_1,list2)
    nx.draw_networkx(subgraph2)
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
