import networkx as nx
import matplotlib.pyplot as plt
import xlsxwriter

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

def ne_node_pict(G,node):
    '''

    :param G: graph
    :param node: which node's neighbors you want to draw
    :return: none
    '''
    R = []
    list1 = list(nx.all_neighbors(G, node))
    print(list1)
    elist = []
    for i in list1:
        elist.append((node,i))
    print(elist)
    list1.insert(0,node)
    subgraph=nx.subgraph(G,list1)
    for i in list1:
        R.append(i)
    nx.draw_networkx_nodes(subgraph,pos=nx.circular_layout(subgraph),node_color='g',node_size=80)
    nx.draw_networkx_edges(subgraph,pos=nx.circular_layout(subgraph),arrows=False)
    label = {}
    for j in list1:
        label[j] = j
    #nx.draw_networkx_labels(G,pos=nx.shell_layout(G),labels=node,font_size=11)
    nx.draw_networkx_labels(G,pos=nx.circular_layout(subgraph),labels=label,font_size=10,font_color='b')
    #nx.draw_networkx_labels(G, pos=nx.circular_layout(list1), labels=label, font_size=12, font_color='r')
    plt.show()


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

    node_Gne(G_1,'1')
    node_Gne(G_dol,'dol')
    node_Gne(G_foot,'foot')
    node_Gne(G_hep,'hep')
    node_Gne(G_kar,'kar')
    node_Gne(G_les,'les')
    node_Gne(G_net,'net')
    node_Gne(G_pol,'pol')
    ne_node_pict(G_1,'1')
