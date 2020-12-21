import networkx as nx
import matplotlib.pyplot as plt
import xlsxwriter
import os
import xlrd
import numpy as np
from sklearn.cluster import KMeans,SpectralClustering
from sklearn import datasets
from multiprocessing import Pool,Process
import os
from scipy.optimize import root

def same_degree(G,name):
    '''

    :param G:Graph
    :param name: xlsx'name
    :return: none
    '''

    sorted_degree_dict = dict(sorted(nx.degree(G),key = lambda x:x[1],reverse=True))
    list1 = list(sorted(set(sorted_degree_dict.values()),reverse=True))
    list2 = list(sorted_degree_dict.keys())
    cont = 0
    conts = 1
    workbook = xlsxwriter.Workbook(name + '-degree.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,'degree')
    worksheet.write(1,0, str(list1[cont]))
    worksheet.write(1,1,str(list2[cont]))
    for key, value in sorted_degree_dict.items():
        if value == list1[cont]:
            worksheet.write(cont+1,conts,key)
            conts += 1
            continue
        if cont < len(list1)-1:
            cont += 1
            worksheet.write(cont+1,0,str(list1[cont]))
            worksheet.write(cont+1,1,key)
            conts = 2
        print(key)
    workbook.close()

def node_Gne(G,name):
    '''

    :param G: graph
    :param name: xlsx's name
    :return: none
    '''
    workbook = xlsxwriter.Workbook(name + '-negigbors.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, '节点')
    i = 1
    j = 1
    for it1 in nx.nodes(G):
        list1=list(nx.all_neighbors(G,it1))
        worksheet.write(i, 0, it1)
        for it2 in list1:
            worksheet.write(i,j,it2)
            worksheet.write(i+1,j,nx.degree(G,it2))
            j+=1
        worksheet.write(i,j,'总数')
        worksheet.write(i,j+1,j-1)
        j=1
        i+=2
    workbook.close()

def ne_node_pict(G,node,dict):
    '''

    :param G: graph
    :param node: which node's neighbors you want to draw
    :return: none
    '''
    R = []
    list1 = list(nx.all_neighbors(G, node))
    elist = []
    for i in list1:
        elist.append((node,i))
    list1.insert(0,node)
    subgraph=nx.subgraph(G,list1)
    for i in list1:
        R.append(i)
    nx.draw_networkx_nodes(subgraph,pos=nx.circular_layout(subgraph),node_color='g',node_size=80)
    nx.draw_networkx_edges(subgraph,pos=nx.circular_layout(subgraph),arrows=False)
    label = {}
    for j in list1:
        label[j] = j
    nx.draw_networkx_labels(G,pos=nx.circular_layout(subgraph),labels=label,font_size=10,font_color='b')
    path = '/Users/mac/Desktop/networkx/'+dict
    if not os.path.exists(path):
        os.makedirs(path)
    plt.savefig(path+'/'+str(node)+'.png')
    plt.close()

def degreeclass_ne(G,file,dict):
    '''
    get the one-neighbor subgraph of the nodes which have the same degree
    :param G:graph
    :param file:path of the degree file
    :param dict:output path
    :return:none
    '''
    workbook = xlrd.open_workbook(file)
    #booknames = workbook.sheet_names()
    mySheet = workbook.sheet_by_name('Sheet1')
    nrows = mySheet.nrows
    for i in range(1,nrows):
        list1 = list(mySheet.row_values(i))
        list1 = [i for i in list1 if i != '']
        test = list1.pop(0)
        print(test)
        for j in list1:
            ne_node_pict(G,j,dict+'/'+str(test))


def node_Gne(G,file,name):
    '''
    nodes classified by degree,find their neighbor nodes and the degree list of neighbor nodes
    :param file: degree file
    :param name: xlsx's name
    :return: none
    '''
    workbook = xlrd.open_workbook(file)
    mySheet = workbook.sheet_by_name('Sheet1')
    nrows = mySheet.nrows
    workbook = xlsxwriter.Workbook(name + '-negigbors.xlsx')
    worksheet1 = workbook.add_worksheet()
    worksheet2 = workbook.add_worksheet()
    worksheet3 = workbook.add_worksheet()
    worksheet4 = workbook.add_worksheet()
    it1 = 0
    for i in range(1, nrows):
        list1 = list(mySheet.row_values(i))
        list1 = [i for i in list1 if i != '']
        test = list1.pop(0)
        worksheet1.write(3*it1+1,0,'degree'+str(test))
        worksheet1.write(3*it1+1,1,'节点数量：'+str(len(list1)))
        worksheet1.write(3*it1+1,2,'所占百分比：{:.2%}'.format(len(list1)/nx.number_of_nodes(G)))
        worksheet2.write(3 * it1 + 1, 0, 'degree' + str(test))
        worksheet3.write(3 * it1 + 1, 0, 'degree' + str(test))
        worksheet4.write(3 * it1 + 1, 0, 'degree' + str(test))
        it1 += 1
        #it2 = 0
        for j in list1:
            worksheet1.write(3*it1,0,'节点'+str(j)+'邻居:')
            worksheet2.write(3 * it1, 0, '节点' + str(j) + '邻居:')
            worksheet3.write(3 * it1, 0, '节点' + str(j) + '邻居:')
            worksheet4.write(3 * it1, 0, '节点' + str(j) + '邻居:')
            list2 = list(nx.all_neighbors(G,j))
            lists = list(list2)
            lists.insert(0,j)
            lists1 = sorted(lists,key = lambda x : nx.degree(G,x),reverse=True)
            subgraph = nx.subgraph(G, lists)
            cont1 = 0
            cont2 = 0
            cont3 = 0
            cont4 = 0
            lists2 = sorted(lists,key = lambda x : nx.degree(subgraph,x),reverse=True)
            lists3 = sorted(lists,key = lambda x : nx.degree(G,x) - nx.degree(subgraph,x),reverse=True)
            lists4 = sorted(lists,key = lambda x : abs(2*nx.degree(subgraph,x)-nx.degree(G,x)),reverse=True)
            for m,n,p,q in zip(lists1,lists2,lists3,lists4):
                cont1 += nx.degree(G,m)
                cont2 += nx.degree(subgraph,n)
                cont3 += nx.degree(G,p) - nx.degree(subgraph,p)
                cont4 += abs(2*nx.degree(subgraph,q)-nx.degree(G,q))
            it2 = 1
            for it in lists1:
                tmp = nx.degree(G,it)
                worksheet1.write(3*it1,it2,it)
                worksheet1.write(3*it1+1,0,'整个网络中的度:')
                worksheet1.write(3*it1+1,it2,tmp)
                if cont1 !=0:
                    worksheet1.write(3*it1+2,0,'P')
                    worksheet1.write(3*it1+2,it2,tmp/cont1)
                it2+=1
            it2=1

            for it in lists2:
                tmp = nx.degree(subgraph, it)
                worksheet2.write(3 * it1, it2, it)
                worksheet2.write(3 * it1 + 1, 0, '一邻居子图中的度:')
                worksheet2.write(3 * it1 + 1, it2,tmp)
                if cont2 !=0:
                    worksheet2.write(3 * it1 + 2, 0, 'P')
                    worksheet2.write(3 * it1 + 2, it2,tmp/cont2)
                it2+=1
            it2 = 1
            for it in lists3:
                tmp = nx.degree(G,it) - nx.degree(subgraph,it)
                worksheet3.write(3 * it1, it2, it)
                worksheet3.write(3 * it1 + 1, 0, '外图中的度:')
                worksheet3.write(3 * it1 + 1, it2, tmp)
                if cont3 != 0:
                    worksheet3.write(3 * it1 + 2, 0, 'P')
                    worksheet3.write(3 * it1 + 2, it2, tmp/cont3)
                it2+=1
            it2 = 1
            for it in lists4:
                tmp = abs(2*nx.degree(subgraph,it)-nx.degree(G,it))
                worksheet4.write(3 * it1, it2, it)
                worksheet4.write(3 * it1 + 1, 0, '内外图度之差的绝对值：')
                worksheet4.write(3 * it1 + 1, it2, tmp)
                if cont4 != 0:
                    worksheet4.write(3 * it1 + 2, 0, 'P')
                    worksheet4.write(3 * it1 + 2, it2,tmp/cont4)
                it2 += 1
            it1 += 1
            #worksheet.write(it+1,it2+1,it2)
    workbook.close()

def hist_pict(G,name):
    '''
    draw the degree picture
    :param G:
    :return:
    '''
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    list1 = list(sorted(sorted_degree_dict.values(), reverse=True))
    list2 = list(sorted(set(sorted_degree_dict.values()), reverse=True))
    plt.hist(list1,bins=len(list1))
    plt.xlabel('degree')
    plt.ylabel('count')
    plt.title('Degree Distribution of ' + name)
    #plt.xticks(list2)
    plt.show()

def degree_cout(G,name):
    '''
    :param G:Graph
    :param name: xlsx'name
    :return: none
    '''

    sorted_degree_dict = dict(sorted(nx.degree(G),key = lambda x:x[1],reverse=True))
    list1 = list(sorted(set(sorted_degree_dict.values()),reverse=True))
    list2 = list(sorted_degree_dict.keys())
    cont = 0
    conts = 0
    workbook = xlsxwriter.Workbook(name + '-degree_cont.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,'degree')
    worksheet.write(0,1,'个数')
    worksheet.write(0,2,'百分比')
    worksheet.write(1,0, str(list1[cont]))
    #worksheet.write(1,1,str(list2[cont]))
    for key, value in sorted_degree_dict.items():
        if value == list1[cont]:
            #worksheet.write(cont+1,conts,key)
            conts += 1
            #print(conts)
            continue
        worksheet.write(cont+1,1,conts)
        worksheet.write(cont+1,2,'{:.4%}'.format(conts/nx.number_of_nodes(G)))
        if cont < len(list1)-1:
            cont += 1
            worksheet.write(cont+1,0,str(list1[cont]))
            #worksheet.write(cont+1,1,key)
            conts = 1
        print(key)
    worksheet.write(cont + 1, 1, conts)
    worksheet.write(cont + 1, 2, '{:.4%}'.format(conts / nx.number_of_nodes(G)))
    workbook.close()

def KM(G,name,k):
    '''
    Kmeans
    :param G:
    :param name:
    :param k:
    :return:
    '''
    workbook = xlsxwriter.Workbook(name + '-km.xlsx')
    worksheet = workbook.add_worksheet()
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    x = np.array(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    #x = np.array(nx.degree(G))
    for i in range(len(x)):
        for j in range(len(x[0])):
            if j == 0:
                x[i][j] = 0
    clf = KMeans(n_clusters=k)
    clf.fit(x)
    centers = clf.cluster_centers_
    labels = clf.labels_
    #print(centers)
    #print(labels)
    k = -1
    it = 1
    worksheet.write(0,0,'类别')
    for i,j in zip(labels,sorted_degree_dict.keys()):
        if i != k:
            k = i
            worksheet.write(k+1,0,'类'+str(k))
            it = 1
        if i == k:
            worksheet.write(k+1,it,j)
            it += 1
            continue
    workbook.close()

def test_k(G,k):
    '''
    get the SSE of the different k
    :param G:
    :param k:
    :return:
    '''
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    x = np.array(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    # x = np.array(nx.degree(G))
    for i in range(len(x)):
        for j in range(len(x[0])):
            if j == 0:
                x[i][j] = 0
    clf = KMeans(n_clusters=k)
    clf.fit(x)
    centers = clf.cluster_centers_
    labels = clf.labels_
    SSE = 0
    k = -1
    it = 1
    for i,j in zip(labels,sorted_degree_dict.values()):
        if i != k:
            k = i
            it = 1
        if i == k:
            SSE += abs(j-centers[i][1])**2
            it += 1
            continue
    return SSE

def k_pict(G):
    '''
    draw the k-SSE's plot
    :param G:
    :return:
    '''
    k = dict()
    for i in range(1, 30):
        k[i] = test_k(G, i)
    print(k)
    x = k.keys()
    y = k.values()
    plt.plot(x, y)
    plt.show()

def dist(a,b):
    '''
    计算样本之间的距离
    :param a:
    :param b:
    :return:
    '''
    sum1 = 0
    sum2 = 0
    for i in a:
        sum1 += i
    for i in b:
        sum2 += i
    sum1 = sum1/len(a)
    sum2 = sum2/len(b)
    return abs(sum1-sum2)

def find_Min(M):
    min = 10000
    x = 0;y = 0
    for i in range(len(M)):
        for j in range(len(M[i])):
            if i != j and M[i][j] < min:
                min = M[i][j];x = i;y = j
    return (x,y,min)

def find_Max(a):
    max = 0
    x = 0
    for i in a:
        j = list()
        j.append(i)
        if max < dist(j,a):
            max = dist(j,a)
            x = i
            a.append(j.pop())
    return x




def R_division(G,dis,name):
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    list1 = list(sorted(sorted_degree_dict.values(), reverse=True))#degree list
    list2 = list(sorted_degree_dict.keys())#id list
    tmp1 = list1[:]
    tmp2 = list2[:]
    workbook = xlsxwriter.Workbook(name +'-' + str(dis) + '-rdivision.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,'度差'+str(dis))
    cont1 = 1
    cont2 = 0
    cont = 0
    while len(list1) != 0:
        worksheet.write(cont1, cont2, '类' + str(cont1))
        tmp = list1[0]
        while len(tmp1) != 0 and tmp - tmp1[0] <= dis and cont2 != 16000:
            cont2 += 1
            worksheet.write(cont1, cont2, tmp2[0])
            tmp2.pop(0)
            tmp1.pop(0)
            list1.pop(0)
        cont1 += 1
        cont2 = 0
    workbook.close()

def R_alldiv(G,dislist,name):
    for i in dislist:
        R_division(G,i,name)

def com(G,k,file,w1,w2):
    '''
    根据粗划分类中的节点个数，类中节点不足的进行合并
    :param G: 图G
    :param k: k匿名中的k值
    :param file: 粗划分类表
    :return:
    '''
    rb = xlrd.open_workbook(file)
    workbook = xlsxwriter.Workbook('test.xlsx')
    worksheet = workbook.add_worksheet()
    mySheet = rb.sheet_by_name('Sheet1')
    nrows = mySheet.nrows
    before = list()
    later = [i for i in list(mySheet.row_values(1)) if i != '']
    later.pop(0)
    a = 0
    worksheet.write(0,0,'合并类')
    for i in range(1,nrows):
        list0 = before[:]
        list1 = later[:]
        if i != nrows - 1:
            list2 = [i for i in list(mySheet.row_values(i + 1)) if i != '']
            list2.pop(0)
        else:
            list2 = []
        if len(list1) < k:
            top = dist_list(G, list1, list0, w1, w2)
            sub = dist_list(G, list1, list2, w1, w2)
            if top < sub:
                list0.extend(list1)
                it = 1
                if len(list0) > k:
                    for j in list0:
                        worksheet.write(a,0,'类')
                        worksheet.write(a,it,j)
                        it += 1
            else:
                list2.extend(list1)
                it = 1
                if len(list2) > k:
                    for j in list2:
                        worksheet.write(i + 1, 0, '类')
                        worksheet.write(i + 1, it, j)
                        it += 1
            before = list0[:]
            later = list2[:]
        else:
            it = 1
            for j in list1:
                worksheet.write(i, 0, '类')
                worksheet.write(i,it,j)
                it += 1
            before = list1[:]
            later = list2[:]
            a = i
    workbook.close()
    return 'test.xlsx'

def dist_list(G,list1,list2,w1,w2):
    '''
    计算两个list之间的指标差
    :param list1: 基类1
    :param list2: 类2
    :return:
    '''
    if len(list2) != 0:
        sumdegree1 = 0
        sumcluster1 = 0
        for i in list1:
            sumdegree1 += nx.degree(G,i)
            sumcluster1 += nx.clustering(G,i)
        sumdegree2 = 0
        sumcluster2 = 0
        for j in list2:
            sumdegree2 += nx.degree(G, j)
            sumcluster2 += nx.clustering(G, j)
        avgdegree1 = sumdegree1/len(list1)
        avgcluster1 = sumcluster1/len(list1)
        avgdegree2 = sumdegree2/len(list2)
        avgcluster2 = sumcluster2/len(list2)
        if avgdegree1 != 0 and avgcluster1 !=0:
            d = w1*abs((avgdegree1 - avgdegree2)/avgdegree1) + w2*abs((avgcluster1 - avgcluster2)/avgcluster1)
        if avgdegree1 == 0:
            d = abs((avgcluster1 - avgcluster2)/avgcluster1)
        if avgcluster1 == 0:
            d = abs((avgdegree1 - avgdegree2)/avgdegree1)

    else:
        d = 2*nx.number_of_nodes(G)
    return d

def dc_list(G,file,sheet):
    '''
    计算两个类之间的指标差
    :param G: 图G
    :param file: 粗划分类表
    :return: 指标列表
    '''
    workbook = xlrd.open_workbook(file)
    mySheet = workbook.sheet_by_name(sheet)
    nrows = mySheet.nrows
    clist = []
    #clist.append((2*nx.number_of_nodes(G),1))
    for i in range(1, nrows):
        list1 = [i for i in list(mySheet.row_values(i)) if i != '']
        list1.pop(0)
        sumdegree = 0
        sumcluster = 0
        for j in list1:
            sumdegree += nx.degree(G,j)
            sumcluster += nx.clustering(G,j)
        d = (sumdegree/len(list1),sumcluster/len(list1))
        clist.append(d)
    #clist.append((2*nx.number_of_nodes(G),1))
    return clist

def comb(G,k,file,w1,w2):
    print('comb the ' + str(file) + ' use '+ str(k) +' anoymous...')
    name = com(G,k,file,w1,w2)
    rb = xlrd.open_workbook(name)
    workbook = xlsxwriter.Workbook('com-' + str(k) + 'anoymous-' + str(file))
    worksheet = workbook.add_worksheet()
    mySheet = rb.sheet_by_name('Sheet1')
    nrows = mySheet.nrows
    cont = 1
    worksheet.write(0,0,'合并类')
    for i in range(1,nrows):
        list1 = [i for i in list(mySheet.row_values(i)) if i != '']
        if len(list1) != 0:
            worksheet.write(cont,0,'类'+str(cont))
            it = 0
            for i in list1:
                worksheet.write(cont,it,i)
                it += 1
            cont += 1
    workbook.close()

def spect_clustering(G):
    '''谱聚类算法'''
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    lists = list()
    for key,value in sorted_degree_dict.items():
        list1 = [key,value]
        lists.append(list1)
    x = np.array(lists,dtype=int)
    list1 = list(sorted(set(sorted_degree_dict.values()), reverse=True))
    list2 = list(sorted_degree_dict.keys())
    from sklearn import metrics
    y_pred = SpectralClustering(n_clusters=22,gamma=0.1).fit_predict(x)
    print(y_pred)
    '''for index,gama in enumerate((0.01,0.1)):
        for index,k in enumerate(range(5,30)):
            y_pred = SpectralClustering(n_clusters=k,gamma=gama).fit_predict(x)
            print("Calinski-Harabasz Score with gama = " + str(gama),
                  "n_clusters = ",k,"score:",metrics.calinski_harabasz_score(x,y_pred))'''

from tqdm import tqdm
def part(G,file,k):
    '''使用KL散度矩阵来对大类进行分裂'''
    print('part the '+ str(file)+' use the KL...')
    workbook = xlrd.open_workbook(file)
    mySheet = workbook.sheet_by_name('Sheet1')
    workbook = xlsxwriter.Workbook('part-' + str(file))
    worksheet1 = workbook.add_worksheet()
    worksheet2 = workbook.add_worksheet()
    worksheet3 = workbook.add_worksheet()
    worksheet4 = workbook.add_worksheet()

    nrows = mySheet.nrows
    row = [1,1,1,1]
    for i in tqdm(range(1,nrows),desc = '大类分裂'):
        list1 = [i for i in list(mySheet.row_values(i)) if i != '']
        str1 = str(list1.pop(0))
        cont = 0

        if(len(list1)<2 * k -1):
            it = 1
            for j in list1:
                worksheet1.write(row[0], it, j)
                worksheet2.write(row[1], it, j)
                worksheet3.write(row[2], it, j)
                worksheet4.write(row[3], it, j)
                it += 1
            row[0] += 1
            row[1] += 1
            row[2] += 1
            row[3] += 1
        else:
            #print('part ' + str1 + ' ' + str(i))
            #print('开始初始化KL散度矩阵。。。。。。')
            m = division(G,list1)
            #print('矩阵初始化完成')
            #print('开始进行分裂写入。。。。。。')
            for n in range(4):
                list_copy = list1[:]
                max = np.max(m[n])
                while np.min(m[n]) != max:
                    col = 0
                    if k % 2 != 0 or k == 2:
                        while col < k:
                            list_m = list(np.argwhere(m[n] == np.min(m[n])))
                            if np.min(m[n]) == max:
                                for l in list_copy:
                                    if l != -1:
                                        if n == 0:
                                            worksheet1.write(row[n], col + 1, l)
                                        elif n == 1:
                                            worksheet2.write(row[n], col + 1, l)
                                        elif n == 2:
                                            worksheet3.write(row[n], col + 1, l)
                                        elif n == 3:
                                            worksheet4.write(row[n], col + 1, l)
                                row[n] += 1
                                break
                            x = list_m[0][0]
                            y = list_m[0][1]
                            m[n][x][:] = max
                            m[n][y][:] = max
                            for i in range(len(list1)):
                                m[n][i][y] = max
                                m[n][i][x] = max
                            close1 = list1[x]
                            close2 = list1[y]
                            list_copy[x] = -1
                            list_copy[y] = -1
                            if n == 0:
                                write_by_k(worksheet1, close1, close2, row[n], col)
                            elif n == 1:
                                write_by_k(worksheet2, close1, close2, row[n], col)
                            elif n == 2:
                                write_by_k(worksheet3, close1, close2, row[n], col)
                            elif n == 3:
                                write_by_k(worksheet4, close1, close2, row[n], col)
                            col += 2
                            '''进度'''
                            cont += 2
                            #print('进度：{:.2%}'.format(cont / (4 * len(list1))))

                        if np.min(m[n]) == max:
                            for l in list_copy:
                                if l != -1:
                                    if n == 0:
                                        worksheet1.write(row[n], col + 1, l)
                                    elif n == 1:
                                        worksheet2.write(row[n], col + 1, l)
                                    elif n == 2:
                                        worksheet3.write(row[n], col + 1, l)
                                    elif n == 3:
                                        worksheet4.write(row[n], col + 1, l)
                                    cont += 1
                                    #print('进度：{:.2%}'.format(cont / (4 * len(list1))))

                        if col >= k:
                            row[n] += 1
                    else:
                        while col <= k:
                            list_m = list(np.argwhere(m[n] == np.min(m[n])))
                            if np.min(m[n]) == max:
                                break
                            x = list_m[0][0]
                            y = list_m[0][1]
                            m[n][x][:] = max
                            m[n][y][:] = max
                            for i in range(len(list1)):
                                m[n][i][y] = max
                                m[n][i][x] = max
                            close1 = list1[x]
                            close2 = list1[y]
                            list_copy[x] = -1
                            list_copy[y] = -1
                            if n == 0:
                                write_by_k(worksheet1, close1, close2, row[n], col)
                            elif n == 1:
                                write_by_k(worksheet2, close1, close2, row[n], col)
                            elif n == 2:
                                write_by_k(worksheet3, close1, close2, row[n], col)
                            elif n == 3:
                                write_by_k(worksheet4, close1, close2, row[n], col)
                            col += 2
                            cont += 2
                            #print('进度：{:.2%}'.format(cont / (4 * len(list1))))
                        if np.min(m[n]) == max:
                            for l in list_copy:
                                if l != -1:
                                    if n == 0:
                                        worksheet1.write(row[n], col + 1, l)
                                    elif n == 1:
                                        worksheet2.write(row[n], col + 1, l)
                                    elif n == 2:
                                        worksheet3.write(row[n], col + 1, l)
                                    elif n == 3:
                                        worksheet4.write(row[n], col + 1, l)

                            row[n] += 1
                            continue

                        if col >= k:
                            row[n] += 1
    for i in range(4):
        for j in range(row[i]):
            if i == 0:
                worksheet1.write(j, 0, '类')
            elif i == 1:
                worksheet2.write(j, 0, '类')
            elif i == 2:
                worksheet3.write(j, 0, '类')
            elif i == 3:
                worksheet4.write(j, 0, '类')
    workbook.close()

def division(G,list1):
    '''使用四种指标来生成KL散度矩阵组合array'''
    p1 = [[]];p2 = [[]];p3 = [[]];p4 = [[]]
    tmp = 0
    #print('开始生成四种指标分布。。。。。。')
    for i in tqdm(list1,desc = '生成四种指标分布'):
        list2 = list(nx.all_neighbors(G,i))[:]
        list2.insert(0,i)
        lists1 = sorted(list2,key = lambda x : nx.degree(G,x),reverse=True)
        subgraph = nx.subgraph(G,lists1)
        lists2 = sorted(list2, key=lambda x: nx.degree(subgraph, x), reverse=True)
        lists3 = sorted(list2, key=lambda x: nx.degree(G, x) - nx.degree(subgraph, x), reverse=True)
        lists4 = sorted(list2, key=lambda x: abs(2 * nx.degree(subgraph, x) - nx.degree(G, x)), reverse=True)
        cont1 = 0;cont2 = 0;cont3 = 0;cont4 = 0
        for m,n,p,q in zip(lists1,lists2,lists3,lists4):
            cont1 += nx.degree(G, m)
            cont2 += nx.degree(subgraph, n)
            cont3 += nx.degree(G, p) - nx.degree(subgraph, p)
            cont4 += abs(2 * nx.degree(subgraph, q) - nx.degree(G, q))
        for it1,it2,it3,it4 in zip(lists1,lists2,lists3,lists4):
            if cont3 == 0:
                p3[tmp].append(1/len(lists3))
            else:
                p3[tmp].append((nx.degree(G,it3)-nx.degree(subgraph,it3))/cont3)
            if cont4 == 0:
                p4[tmp].append((1/len(lists4)))
            else:
                p4[tmp].append((abs(2*nx.degree(subgraph,it4)-nx.degree(G,it4)))/cont4)
            p1[tmp].append(nx.degree(G,it1)/cont1)
            p2[tmp].append(nx.degree(subgraph,it2)/cont2)
        p1.append([]);p2.append([]);p3.append([]);p4.append([])
        tmp += 1
        #print('进度：{:.2%}'.format(tmp/len(list1)))
    #print('四种指标分布生成完毕')
    p1.pop();p2.pop();p3.pop();p4.pop()
    #print('开始生成KL散度矩阵1。。。。。。')
    matrix1 = matrix_gen(p1,tmp)
    #print('开始生成KL散度矩阵2。。。。。。')
    matrix2 = matrix_gen(p2,tmp)
    #print('开始生成KL散度矩阵3。。。。。。')
    matrix3 = matrix_gen(p3,tmp)
    #print('开始生成KL散度矩阵4。。。。。。')
    matrix4 = matrix_gen(p4,tmp)
    matrix123 = (matrix1 + matrix2 + matrix3) / 3
    matrix1234 = (matrix1 + matrix2 + matrix3 + matrix4) / 4
    matrix234 = (matrix2 + matrix3 + matrix4) / 3
    return np.array([matrix1,matrix123,matrix1234,matrix234])



import scipy.stats
import math

def cont_KL(list1,list2):
    a = abs(len(list1)-len(list2))
    if a != 0:
        if len(list1) < len(list2):
            for i in range(a):
                list1.append(0)
        else:
            for i in range(a):
                list2.append(0)
    KL1 = 0;KL2 = 0
    for i in range(len(list1)):
        if list2[i] != 0 and list1[i] != 0:
            KL1 += list1[i] * np.log(list1[i] / list2[i])
            KL2 += list2[i] * np.log(list2[i] / list1[i])
        else:
            KL1 += 0
            KL2 += 0
    return (KL1+KL2)/2

def matrix_gen(list1,length):
    matrix = np.random.rand(length,length)
    matrix.reshape(length,length)
    cont = 0
    for i in tqdm(range(length),desc = '生成KL矩阵'):
        for j in range(i + 1,length):
            matrix[i][j] = cont_KL(list1[i],list1[j])
            cont += 1
            #print('进度：{:.2%}'.format(cont / length**2))
    max = np.max(matrix)
    row,col = np.diag_indices_from(matrix)
    matrix[row,col] = max + 1
    for i in range(length):
        for j in range(i+1):
            matrix[i][j] = max + 1
            cont += 1
            #print('进度：{:.2%}'.format(cont / length ** 2))
    return matrix

def write_by_k(worksheet,close1,close2,row,col):
    worksheet.write(row,col + 1,close1)
    worksheet.write(row,col + 2,close2)

def part_comb(G,k,file,w1,w2):
    print('comb the ' + str(file))
    workbook = xlrd.open_workbook(file)
    mySheet1 = workbook.sheet_by_name('Sheet1')
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    workbook = xlsxwriter.Workbook('test1.xlsx')
    worksheet1 = workbook.add_worksheet()
    worksheet2 = workbook.add_worksheet()
    worksheet3 = workbook.add_worksheet()
    worksheet4 = workbook.add_worksheet()
    klist1 = part_comby_sheet(k, mySheet1, worksheet1)
    klist2 = part_comby_sheet(k, mySheet2, worksheet2)
    klist3 = part_comby_sheet(k, mySheet3, worksheet3)
    klist4 = part_comby_sheet(k, mySheet4, worksheet4)
    workbook.close()
    add_clist(G, k, klist1, klist2, klist3, klist4, w1, w2, file)

def part_comby_sheet(k,mySheet,worksheet):
    klist = []
    nrows = mySheet.nrows
    row = 1
    for i in range(1,nrows):
        list1 = [i for i in list(mySheet.row_values(i)) if i != '']
        list1.pop(0)
        if len(list1) >= k:
            col = 1
            for j in list1:
                worksheet.write(row,col,j)
                col += 1
            row += 1
        else:
            klist.append(list1)
    return klist

def add_clist(G,k,klist1,klist2,klist3,klist4,w1,w2,file):
    clist1 = dc_list(G, 'test1.xlsx','Sheet1')
    clist2 = dc_list(G, 'test1.xlsx','Sheet2')
    clist3 = dc_list(G, 'test1.xlsx','Sheet3')
    clist4 = dc_list(G, 'test1.xlsx','Sheet4')
    workbook = xlrd.open_workbook('test1.xlsx')
    mySheet1 = workbook.sheet_by_name('Sheet1')
    mySheet2 = workbook.sheet_by_name('Sheet2')
    mySheet3 = workbook.sheet_by_name('Sheet3')
    mySheet4 = workbook.sheet_by_name('Sheet4')
    workbook = xlsxwriter.Workbook('com-' + str(file))
    worksheet1 = workbook.add_worksheet()
    worksheet2 = workbook.add_worksheet()
    worksheet3 = workbook.add_worksheet()
    worksheet4 = workbook.add_worksheet()
    read_sheet(mySheet1,worksheet1,k)
    read_sheet(mySheet2,worksheet2,k)
    read_sheet(mySheet3,worksheet3,k)
    read_sheet(mySheet4,worksheet4,k)
    add_clistby_sheet(G, k, klist1, clist1, w1, w2, mySheet1, worksheet1)
    add_clistby_sheet(G, k, klist2, clist2, w1, w2, mySheet2, worksheet2)
    add_clistby_sheet(G, k, klist3, clist3, w1, w2, mySheet3, worksheet3)
    add_clistby_sheet(G, k, klist4, clist4, w1, w2, mySheet4, worksheet4)
    workbook.close()

def add_clistby_sheet(G,k,klist,clist,w1,w2,mysheet,worksheet):
    #print(mysheet)
    len_list = []
    for m in range(1, mysheet.nrows):
        list_m = [i for i in list(mysheet.row_values(m)) if i != '']
        len_list.append(len(list_m))
    for i in klist:
        for j in i:
            mlist = []
            d1 = (nx.degree(G,j),nx.clustering(G,j))
            for n in clist:
                if d1[0] != 0 and d1[1] != 0:
                    d = w1 * abs((d1[0] - n[0]) / d1[0]) + w2 * abs(
                        (d1[1] - n[1]) / d1[1])
                if d1[0] == 0:
                    d = abs((d1[1] - n[1]) / d1[1])
                if d1[1] == 0:
                    d = abs((d1[0] - n[0]) / d1[0])
                mlist.append(d)
            min_m = min(mlist)
            index_m = mlist.index(min_m)
            while len_list[index_m] >= 2 * k - 1:
                mlist[index_m] = max(mlist)
                min_m = min(mlist)
                index_m = mlist.index(min_m)
            worksheet.write(index_m + 1, len_list[index_m] + 1, j)
            len_list[index_m] += 1



def read_sheet(mysheet,worksheet,k):
    nrows = mysheet.nrows
    row = 1
    for i in range(1, nrows):
        list1 = [i for i in list(mysheet.row_values(i)) if i != '']
        if len(list1) >= k:
            col = 1
            for j in list1:
                worksheet.write(row,col,j)
                col += 1
            row += 1


def func(G,name,file):
    workbook = xlrd.open_workbook(file)
    mySheet = workbook.sheet_by_name('Sheet1')
    cont_list = mySheet.col_values(1)
    cont_list.pop(0)
    set_cont_list = list(set(cont_list))
    sorted_set_cont_list = list(sorted(set(cont_list)))
    mid = sorted_set_cont_list[len(sorted_set_cont_list)//2]
    #print(cont_list)
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    # list1 = list(sorted(set(sorted_degree_dict.values()), reverse=True))
    #y = list(sorted(set(sorted_degree_dict.values()), reverse=True))
    x = list(sorted(set(sorted_degree_dict.values())))
    y = cont_list[:]
    y.reverse()
    index = y.index(mid)
    x = x[index+1:]
    y = y[index+1:]
    #y =
    #y = list(sorted(sorted_degree_dict.values(), reverse=True))
    #x = [i for i in range(1, len(y) + 1)]
    f1 = np.polyfit(x, y, 5)
    #print('f1 is:', f1)
    p1 = np.poly1d(f1)
    #print('p1 is :\n', p1)
    yvals = p1(x)  # 拟合y值
    p2 = np.polyder(p1, 1)#一阶导数
    #print('p2 is:\n', p2)
    p3 = np.polyder(p1,2)
    yvals1 = p2(x)
    yvals2 = p3(x)

    #print('yvals is :\n', yvals)
    # 绘图
    plt.figure(figsize=(20,10))
    plot1 = plt.plot(x, y, 's', label='original values')
    plot2 = plt.plot(x, yvals, 'r', label='polyfit values')
    #plot3 = plt.plot(x, yvals1,'g',label = 'polyder values')
    #plot3 = plt.plot(x, yvals2,'y',label = 'polyder2 values')
    my_x_ticks = np.arange(0, 140, 5)
    plt.xticks(my_x_ticks)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(loc=4)  # 指定legend的位置右下角
    plt.title('polyfitting of ' + name)
    solution2 = root(fun=p3, x0=[1,2,3])
    solution = root(fun=p2, x0=[1,30,50,75,85])
    #list_2 = list[i for i in list(p3(solution.x))]
    list_2 = []

    for i in range(len(solution.x)):
        if p3(solution.x[i]) > 0:
            list_2.append([solution.x[i],p3(solution.x[i])])
    sorted_list = sorted(list_2,key=lambda x:x[1],reverse=True)
    print(sorted_list)
    path = '/Users/mac/Desktop/networkx/'
    plt.savefig(path + '/' + name + '.png')
    plt.show()
    #print(solution.x[0])
    #print(solution2.x[0])
    #print(p1(solution.x[0]))
    #print(p1(solution.x[0]))
    #print(solution.x)
    #print(p1(solution.x[0]))
    #print(solution2.x[0])
    #print(p1(solution2.x[0]))
    return p1(solution2.x[0])

def draw_pict_dependon_degree(G,name):
    G = nx.to_undirected(G)
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    list1 = list(sorted(sorted_degree_dict.values(), reverse=True))
    list2 = list(sorted_degree_dict.keys())
    #print(list2)
    degree1 = func(G,name)
    cont = 0
    for i in list1:
        if i > degree1:
            cont += 1
        else:
            break
    plt.figure(figsize=(20,10))
    bigger_list = list2[:int(cont)+1]
    print('bigger_list:',bigger_list)
    print('len:',len(bigger_list))
    smaller_list = list2[int(cont)+1:]
    pos = nx.spring_layout(G,k=1.0)
    #nx.draw_networkx_nodes(subgraph, pos=nx.circular_layout(subgraph), node_color='g', node_size=80)
    #nx.draw_networkx_edges(subgraph, pos=nx.circular_layout(subgraph), arrows=False)
    #plot1 = nx.draw_networkx(G,pos=nx.spring_layout(G),nodelist = bigger_list,edgelist = None,node_color = 'g',with_labels=True)
    #plot2 = nx.draw_networkx(G,pos=nx.spring_layout(G),nodelist = smaller_list,edgelist = None,node_color = 'b',with_labels=True)
    plot3 = nx.draw_networkx_nodes(G,pos,nodelist=bigger_list,node_size=120,node_color='g')
    plot4 = nx.draw_networkx_nodes(G,pos,nodelist=smaller_list,node_size=100,node_color='y')
    plot5 = nx.draw_networkx_edges(G,pos,alpha=0.4,width=0.5)
    plot6 = nx.draw_networkx_labels(G,pos,font_size=7)
    plt.title(name)
    plt.show()
    Gs = nx.random_geometric_graph

def get_bigger_percent(G,name):
    sorted_degree_dict = dict(sorted(nx.degree(G), key=lambda x: x[1], reverse=True))
    list1 = list(sorted(sorted_degree_dict.values(), reverse=True))
    list2 = list(sorted_degree_dict.keys())
    # print(list2)
    degree1 = func(G,name)
    cont = 0
    for i in list1:
        if i > degree1:
            cont += 1
        else:
            break
    print('cont:',cont)
    print('number of nodes:',nx.number_of_nodes(G))
    return format(cont/nx.number_of_nodes(G),'.8f')

def G_id(G,name):
    '''图的节点按照id从零开始编号，生成一系列文件'''
    G_un = G.to_undirected()
    G_id = nx.convert_node_labels_to_integers(G_un)
    same_degree(G,name)
    R_division(G_id, 3, name)
    comb(G_id,3,name+'-3-rdivision.xlsx',0.5,0.5)
    comb(G_id,4,name+'-3-rdivision.xlsx',0.5,0.5)
    part(G_id,'com-3anoymous-' + name + '-3-rdivision.xlsx',3)
    part(G_id,'com-4anoymous-' + name + '-3-rdivision.xlsx',4)
    part_comb(G_id,3,'part-com-3anoymous-' + name + '-3-rdivision.xlsx',0.5,0.5)
    part_comb(G_id,4,'part-com-4anoymous-' + name + '-3-rdivision.xlsx',0.5,0.5)

if __name__ == '__main__':
    G_1 = nx.read_gml('1.gml',label=None)
    G_dol = nx.read_gml('dolphins.gml')
    G_foot = nx.read_gml('football.gml')
    G_hep = nx.read_gml('hep-th.gml')
    G_kar = nx.read_gml('karate.gml', label=None, destringizer=None)
    G_les = nx.read_gml('lesmis.gml')
    G_net = nx.read_gml('netscience.gml')
    G_pol = nx.read_gml('polbooks.gml')
    G_HepPh = nx.read_edgelist('CA-HepPh.txt')
    G_HepTh = nx.read_edgelist('CA-HepTh.txt')
    #G_lj = nx.read_edgelist('com-lj.ungraph.txt')
    G_Email = nx.read_edgelist('Email-Enron.txt')
    #draw_pict_dependon_degree(G_net,'G_1')
    G_list = [G_1,G_dol,G_foot,G_kar,G_les,G_net,G_pol,G_HepPh,G_HepTh,G_Email]
    G_name_list = ['G_1', 'G_dol', 'G_foot', 'G_kar', 'G_les', 'G_net', 'G_pol', 'G_HepPh', 'G_HepTh', 'G_Email']
    test = ['106','214','213','259']
    #R_division(G_1, 3, '1-id')
    #comb(G_1,3,'1-id-3-rdivision.xlsx',0.5,0.5)
    #comb(G_1,4,'1-id-3-rdivision.xlsx',0.5,0.5)
    #comb(G_1,10,'1-3-rdivision.xlsx',0.5,0.5)
    #comb(G_1,6,'1-3-rdivision.xlsx',0.5,0.5)
    #node_Gne(G_1,'com-3anoymous-1-3-rdivision.xlsx','1-3anoymous')
    #part(G_1,'com-3anoymous-1-id-3-rdivision.xlsx',3)
    #part(G_1,'com-4anoymous-1-id-3-rdivision.xlsx',4)
    #part(G_1,'com-10anoymous-1-3-rdivision.xlsx',10)
    #part_comb(G_1,3,'part-com-3anoymous-1-id-3-rdivision.xlsx',0.5,0.5)
    #part_comb(G_1,4,'part-com-4anoymous-1-id-3-rdivision.xlsx',0.5,0.5)
    #part_comb(G_1,10,'part-com-10anoymous-1-3-rdivision.xlsx',0.5,0.5)
