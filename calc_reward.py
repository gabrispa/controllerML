import pandas as pd
import csv
from get_dict import normalize, normalize_path_cost

def calc_reward_avg(routes_complete):
    avg_reward_for_episode  = {}
    data = pd.read_csv("./net_info.csv")
    #print(data.loc[(data["node1"] == 1) & (data["node2"] == 7)]

    file_rewards = open('./rewards_history', 'w')
    header_ = ['episode','reward', 'avg_bwd', 'avg_delay', 'avg_loss']
    file = csv.writer(file_rewards, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    file.writerow(header_)
    
    for episode in range(len(routes_complete[1][2])):
        reward = 0
        bwd = 0
        delay = 0
        loss = 0
        num_paths = 0
        for src in range(1, len(routes_complete)+1):
            for dst in range(1, len(routes_complete[src])+2):
                if src != dst:
                    #print(routes_complete[src][dst][episode])
                    num_paths += 1
                    
                    reward += calc_reward(routes_complete[src][dst][episode], data, src, dst)
                    bwd_tmp, delay_tmp, loss_tmp = calc_avg_stats_path(routes_complete[src][dst][episode], data)
                    bwd += bwd_tmp
                    delay += delay_tmp
                    loss += loss_tmp
                    #print("Completato episodio ", episode +1, " per ", src, " ", dst)
        print("REWARD EPISODIO ", episode + 1, " = ", float(reward/num_paths))
        print("AVG BDW: ", round(float(bwd/num_paths),2))
        print("AVG DELAY: ", round(float(delay/num_paths),2))
        print("AVG LOSS: ", round(float(loss/num_paths),2), "\n\n")
        file.writerow([episode + 1, round(float(reward/num_paths),2), round(float(bwd/num_paths),2),
            round(float(delay/num_paths),2), round(float(loss/num_paths),2)])
        
                    
def calc_reward(route, data, src, dst):
    r = 0
    #if route[-1] != dst:
    #   r = 1000
    #   return r
    for hop in range(0, len(route)-1):#len(route)):
        
        row = data.loc[(data["node1"] == route[hop]) & (data["node2"] == route[hop+1])]
        if row.empty:
            row = data.loc[(data["node2"] == route[hop]) & (data["node1"] == route[hop+1])]
        if not row.empty:
            #print(row)
            bwd_n, delay_n, pkloss_n = normalize_path_cost(row["bwd"], row["delay"], row["pkloss"])
            #print(bwd_n)
            r += bwd_n[0] + delay_n[0] + pkloss_n[0]
    
    return r
    
def calc_avg_stats_path(route, data):
    avg_bwd = 0
    avg_loss = 0
    avg_delay = 0
    n_hops = len(route)-1
    #print(route)
    for hop in range(0, n_hops):
        row = data.loc[(data["node1"] == route[hop]) & (data["node2"] == route[hop+1])]
        if row.empty:
            row = data.loc[(data["node2"] == route[hop]) & (data["node1"] == route[hop+1])]
            
        #print(row)
        if not row.empty:
            avg_bwd += float(row["bwd"])
            avg_delay += float(row["delay"])
            avg_loss += float(row["pkloss"])
            
    #print(avg_bwd,"\n", avg_delay, "\n", avg_loss, "\n\n")
    return float(avg_bwd/n_hops), float(avg_delay/n_hops), float(avg_loss/n_hops)
    
        
        
