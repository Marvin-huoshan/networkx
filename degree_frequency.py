import networkx as nx
import numpy as np
import xlwt
import pandas as pd
import xlsxwriter

def sortedgetdegreeview(a):
    dict_a=dict(nx.degree(a))
    for key,values in dict_a.items():
        dict_a[key] = int(values)
    sort_dict = dict(sorted(dict_a.items(),key=lambda x:x[1]))
    return sort_dict
def degree_frequency(x,s):
    dict_sum=dict()
    iter = 0
    cont = 0
    mark = 0
    for key, value in x.items():
        while value != iter:
            cont=0
            mark = 0
            iter+=1
        dict_sum[str(value)]=cont+1
        if value == iter and mark == 0:
            print("degree" + str(value) + " :")
            mark = 1
        if value == iter:
            cont+=1
            print(str(key) + " ")
            continue
        #dict_sum[str(value)]=cont
        cont = 0
    print(dict_sum)
    workbook = xlsxwriter.Workbook(s+'.xlsx')
    worksheet = workbook.add_worksheet()
    i=1
    worksheet.write(0,0,'度数')
    worksheet.write(0,1,'个数')
    for key,value in dict_sum.items():
        worksheet.write(i,0,str(key))
        worksheet.write(i,1,str(value))
        i+=1
    workbook.close()



if __name__ == '__main__':
    G_1 = nx.read_gml('/Users/mac/PycharmProjects/networkx/1.gml')
    # G_cel = nx.read_gml('/Users/mac/PycharmProjects/networkx/celegansneural.gml', label=None, destringizer=None)
    G_dol = nx.read_gml('/Users/mac/PycharmProjects/networkx/dolphins.gml')
    G_foot = nx.read_gml('/Users/mac/PycharmProjects/networkx/football.gml')
    G_hep = nx.read_gml('/Users/mac/PycharmProjects/networkx/hep-th.gml')
    G_kar = nx.read_gml('/Users/mac/PycharmProjects/networkx/karate.gml', label=None, destringizer=None)
    G_les = nx.read_gml('/Users/mac/PycharmProjects/networkx/lesmis.gml')
    G_net = nx.read_gml('/Users/mac/PycharmProjects/networkx/netscience.gml')
    G_pol = nx.read_gml('/Users/mac/PycharmProjects/networkx/polbooks.gml')
    degree_G_1 = sortedgetdegreeview(G_1)
    degree_G_dol = sortedgetdegreeview(G_dol)
    degree_G_foot = sortedgetdegreeview(G_foot)
    degree_G_hep = sortedgetdegreeview(G_hep)
    degree_G_kar = sortedgetdegreeview(G_kar)
    degree_G_les = sortedgetdegreeview(G_les)
    degree_G_net = sortedgetdegreeview(G_net)
    degree_G_pol = sortedgetdegreeview(G_pol)
    #degree_frequency(degree_G_1,'1')
    #degree_frequency(degree_G_dol,'dol')
    degree_frequency(degree_G_foot,'foot')
    #degree_frequency(degree_G_hep,'hep')
    #degree_frequency(degree_G_kar,'kar')
    #degree_frequency(degree_G_les,'les')
    #degree_frequency(degree_G_net,'net')
    #degree_frequency(degree_G_pol,'pol')
