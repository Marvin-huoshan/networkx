import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

G=nx.read_gml('/Users/mac/PycharmProjects/networkx/karate.gml',label=None,destringizer=None)
nx.draw(G)
#plt.show()

print(nx.edges(G))
print(nx.nodes(G))
print(nx.degree(G))

degree_dict = {[i for i in G.nodes][n]: [len(G[i]) for i in G.nodes][n] for n in range(len(G.nodes()))} # 字典解析获得度列表
print(degree_dict)
print(G.degree())
#度相同的分类、度差一差二的分类、k-means分类、节点的聚类系数分类
print(G.degree([1, 2]))
print(G.degree()[1])
#度排序
sorted_degree_dict = dict(sorted(degree_dict.items(),key=lambda x:x[1]))
node_list=list(sorted_degree_dict.keys())
print(sorted_degree_dict)
#度相同分类
cont=1
print("degree:" + str(cont) + " :")
for key,value in sorted_degree_dict.items():
    if value == cont:
        print(str(key)+" ")
        continue
    cont += 1
    print("degree:" + str(cont) + " :" )
    print(str(key))

#度差一差二分类
def cont_dif(i,j):
    """

    :param i:node index i
    :param j: node index j
    :return: distence of node i and node j
    """
    d_i=sorted_degree_dict[node_list[i]]
    d_j=sorted_degree_dict[node_list[j]]
    return d_i-d_j

list1=list()
list2=list()

def node_dist():
    fist=0
    while (fist!=len(G.nodes)-1):
        for n in range(len(G.nodes)):
            if cont_dif(fist,n)==1:
                tmp=(node_list[fist],node_list[n])
                list1.append(tmp)
            if cont_dif(fist,n)==2:
                tmp=(node_list[fist],node_list[n])
                list2.append((tmp))
        fist+=1
    print("度相差一节点：")
    print(list1)
    print("度相差二节点：")
    print(list2)

node_dist()
print(G.degree)
print(G.degree[1])
x=np.array(G.degree)
print(x)
print(x[:,1])
#plt.scatter(x[:,0],x[:,1])

#plt.show()

kmeans=KMeans(n_clusters=3,random_state=0).fit(x)
labels=kmeans.labels_
center=kmeans.cluster_centers_
print(center)
print(labels)
'''
for i in range(len(labels)):
    if labels[i]==0:
        plt.scatter(x[i][0], x[i][1], c='b')
    elif labels[i]==1:
        plt.scatter(x[i][0], x[i][1], c='r')
    else:
        plt.scatter(x[i][0], x[i][1], c='y')
plt.scatter(center[:,0],center[:,1],marker='*', c=('g'),s=100)
'''
#plt.show()

#节点的聚类系数分类
print(nx.clustering(G))
cluster=nx.clustering(G)
#degree_dict = {[i for i in G.nodes][n]: [len(G[i]) for i in G.nodes][n] for n in range(len(G.nodes()))}
print(G.nodes)
#y=np.array([i for i in ])
dlist=list()
for key,values in cluster.items():
    tmp=[key,values]
    dlist.append(tmp)
#print(dlist)
cluster_array=np.array(dlist)
print(cluster_array)
kmeans_cluster=KMeans(n_clusters=4,random_state=0).fit(cluster_array)
labels_cluster=kmeans_cluster.labels_
center_cluster=kmeans_cluster.cluster_centers_
print(labels_cluster)
print(center_cluster)
for i in range(len(labels_cluster)):
    if labels_cluster[i]==0:
        plt.scatter(x[i][0],x[i][1],c='b')
    elif labels_cluster[i]==1:
        plt.scatter(x[i][0],x[i][1],c='r')
    elif labels_cluster[i]==2:
        plt.scatter(x[i][0],x[i][1],c='g')
    else:
        plt.scatter(x[i][0],x[i][1],c='y')
plt.scatter(center_cluster[:,0],center_cluster[:,1],marker='*',c='orange',s=100)
plt.show()
