import copy
import numpy as np
def rand_number(seed):
    m = 2^34
    c = 251
    a = 4*c +1
    b = 351
    return ((a*seed+b)%m)/m

def gaussian(x, mu, sig):
    return round(np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.))), 3)

def initial_R(A,Z,weight,A_Z_dict):
    #input net is
    R = {}
    net = copy.deepcopy(A_Z_dict)
    for i in net.keys():  #for each switch
        sub_key = net[i]   #sub_key contiene i neighbors dello switch i-esimo
        sub_dic = {}
        for j in sub_key:   #per ogni neighbour
            sub_dic[j] = 0
        R[i] = sub_dic       #La R dello switch i-esimo è un dict che ad ogni neighbour associa 0 
    for i in range(len(A)):
        R[A[i]][Z[i]] = weight[i]   #Riempie R
    return R  

def initial_Q(R):
    seed = np.random.randint(0, 100)
    Q = copy.deepcopy(R)
    for i in Q.keys():  #per ogni switch
        for j in Q[i].keys():   #per ogni neighbour
            # Q[i][j] = rand_number(seed)
            Q[i][j] = 0
    return Q
    
 
