import pandas as pd
import csv

def calc_reward_avg(routes_complete):
    avg_reward_for_episode  = {}
    data = pd.read_csv("./net_info.csv")
    #print(data.loc[(data["node1"] == 1) & (data["node2"] == 7)]

    file_rewards = open('./rewards_history', 'w')
    header_ = ['episode','reward']
    file = csv.writer(file_rewards, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    file.writerow(header_)
    
    for episode in range(len(routes_complete[1][2])):
        reward = 0
        num_paths = 0
        for src in range(1, len(routes_complete)+1):
            for dst in range(1, len(routes_complete[src])+2):
                if src != dst:
                    #print(routes_complete[src][dst][episode])
                    num_paths += 1
                    
                    reward += calc_reward(routes_complete[src][dst][episode], data, src, dst)
        #print("Reward episodio ", episode + 1, " = ", float(reward/num_paths), "\n")
        file.writerow([episode + 1, round(float(reward/num_paths),2)])
        
                    
def calc_reward(route, data, src, dst):
    r = 0
    if route[-1] != dst:
       r = 1000
       return r
    for hop in range(1):#len(route)):
        row = data.loc[(data["node1"] == route[hop]) & (data["node2"] == route[hop+1])]
        if not row.empty:
            #print(row)
            bwd_n, delay_n, pkloss_n = normalize_path_cost(row["bwd"], row["delay"], row["pkloss"])
            #print(bwd_n)
            r += bwd_n[0] + delay_n[0] + pkloss_n[0]
        else:
            r = 1000
        
    return r
        
        
def normalize_path_cost(bwd, delay, pkloss):
    '''
    Normalize values for reward.
    '''

    bwd_cost = [] #since the RL will minimize reward function, we do 1/bwd for such function
    for val in bwd:
        if val > 0.005: #ensure minimum bwd available
            temp = 1/val
            bwd_cost.append(round(temp, 6))
        else:
            bwd_cost.append(1/0.005)

    bwd_n = [normalize(bwd_val, 0, 100, min(bwd_cost), max(bwd_cost)) for bwd_val in bwd_cost]
    delay_n = [normalize(delay_val, 0, 100, min(delay), max(delay)) for delay_val in delay]
    pkloss_n = [normalize(pkloss_val, 0, 100, min(pkloss), max(pkloss)) for pkloss_val in pkloss]
    return bwd_n, delay_n, pkloss_n
    
def normalize(value, minD, maxD, min_val, max_val):
    if max_val == min_val:
        value_n = (maxD + minD) / 2
    else:
        value_n = (maxD - minD) * (value - min_val) / (max_val - min_val) + minD
    return value_n
