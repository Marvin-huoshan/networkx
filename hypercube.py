import random
routes = [[1 for i in range(5)] for i in range(5)]
digs = [3,5,7,11,13]
digss = [random.sample(digs,len(digs))for i in range(5)]
#print(digss)
tmp = [1,1,1,1,1]
def tmp_equal(loca,num):
    tmps = tmp[loca] * num
    for i in range(5):
        if (tmps == tmp[i]) and tmps != 15015:
            return False
    tmp[loca] *= num
    return True

def route_hypercube(k):
    j = 0
    it = 0
    if k == 5 :
        return 0
    for i in range(5):
        while j < len(digss[i]) and it < 10:
            '''tmp[i] *= routes[i][k]
            if tmp'''
            if tmp_equal(i,digss[i][j]):
                routes[i][k] = digss[i].pop(j)
                break
            else: j = (j+1)%len(digss[i])
            it += 1

    route_hypercube(k+1)

if __name__ == '__main__':
    route_hypercube(0)
    print(routes)
    print(tmp)





