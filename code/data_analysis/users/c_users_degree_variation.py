import networkx as nx
from tqdm import tqdm
import json
import numpy as np


def average_new_neighbor_degree(node,graph_after,graph_before):
    set_x = set(graph_after.neighbors(node))
    set_y = set(graph_before.neighbors(node))
    new_neighbors = [x for x in set_x if x not in set_y]
    new_degree_mean = np.mean([graph_after.degree(node) for node in new_neighbors])
    return new_degree_mean


def variation_neighborhood_of_my_neighbors(node,graph_after,graph_before):
    set_x = set(graph_after.neighbors(node))
    set_y = set(graph_before.neighbors(node))
    neighbors = set_x.intersection(set_y)
    if len(neighbors) == 0:
        return 0.0
    else:
        v = 0.0
        for neighbor in neighbors:
            set_x = set(graph_after.neighbors(neighbor))
            set_y = set(graph_before.neighbors(neighbor))
            nominator = set_x.intersection(set_y)
            denominator = set_x.union(set_y)
            v += len(nominator)/len(denominator)
        return v/len(neighbors)


def variation_of_degree_neighbors(node,graph_before,graph_after):
    d_after = nx.average_neighbor_degree(graph_after,nodes =[node])
    d_before = nx.average_neighbor_degree(graph_before,nodes =[node])
    v = (d_after[node] - d_before[node])/d_before[node]
    return v


def variation_neighborhood(node,graph_after,graph_before):
    set_x = set(graph_after.neighbors(node))
    set_y = set(graph_before.neighbors(node))
    nominator = set_x.intersection(set_y)
    denominator = set_x.union(set_y)
    return len(nominator)/len(denominator)


def variation_degree(node,graph_after,graph_before):
    d_after = graph_after.degree(node)
    d_before = graph_before.degree(node)
    v = (d_after - d_before)/d_before
    return v


def variation(kind,year_weeks_couple,output_data,data_users):
    year_week_tuple = year_weeks_couple[0]
    year = year_week_tuple[0]
    week = year_week_tuple[1]
    year_week = str(year)+"_"+str(week)
    users_before = set(data_users[year_week].keys())
    graph_before = nx.read_gpickle("data/network/network_user_filter_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
    year_week_tuple = year_weeks_couple[1]
    year = year_week_tuple[0]
    week = year_week_tuple[1]
    year_week = str(year)+"_"+str(week)
    users_after = set(data_users[year_week].keys())
    graph_after = nx.read_gpickle("data/network/network_user_filter_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
    #common nodes
    nodes_after = set(graph_after.nodes()).intersection(users_after)
    nodes_before = set(graph_before.nodes()).intersection(users_before)
    common_nodes = list(nodes_after.intersection(nodes_before))
    #degree variation
    dict_nodes = {node:{
                        "degree_variation":variation_degree(node,graph_after,graph_before),
                        "neighboorhood_variation":variation_neighborhood(node,graph_after,graph_before),
                        "degree_before":graph_before.degree(node),
                        "degree_now":graph_after.degree(node),
                        "knn_before":nx.average_neighbor_degree(graph_before,nodes =[node])[node],
                        "knn_now":nx.average_neighbor_degree(graph_after,nodes =[node])[node],
                        "variation_neighborhood_of_my_neighbors":variation_neighborhood_of_my_neighbors(node,graph_after,graph_before),
                        "variation_of_degree_neighbors":variation_of_degree_neighbors(node,graph_after,graph_before),
                        "new_neighbors_knn":average_new_neighbor_degree(node,graph_after,graph_before)
                        } for node in common_nodes}
    output_data[year_week] = dict_nodes
    return output_data


def main(kind):
    kind = kind.replace(' ','_').lower()
    output_data = {}
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    year_weeks_couple = [[year_weeks[i],year_weeks[i+1]] for i in range(0,len(year_weeks)-1)]
    with open("data/users/users_gyration_w2v_"+kind+".json","r") as inpuf:
        data_users = json.load(inpuf)
    for year_weeks_c in tqdm(year_weeks_couple):
        output_data = variation(kind,year_weeks_c,output_data,data_users)
    with open("data/users/users_degree_"+kind+".json","w") as outpuf:
        json.dump(output_data,outpuf)


main("politics")
#main("nba")
#main("nfl")
#main("europe")
