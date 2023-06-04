import networkx as nx
from tqdm import tqdm


def disparity_integral(p,k):
	"""
	calculate the definite integral for the PDF in the disparity filter
	"""
	return (1-p)**(k-1)


def disparity_filter(graph):
	"""
	implements a disparity filter, based on multiscale backbone networks
	https://arxiv.org/pdf/0904.2389.pdf
	"""
	for node in graph.nodes():
		node_placer = graph.nodes[node]
		degree_in = graph.in_degree(node)
		degree_out = graph.out_degree(node)
		strenght_in = 0.0
		strenght_out = 0.0

		for out_neighbor in graph.successors(node):
			strenght_out += graph.edges[(node,out_neighbor)]["weight"]
		for in_neighbor in graph.predecessors(node):
			strenght_in += graph.edges[(in_neighbor,node)]["weight"]

		node_placer["strenght_in"] = strenght_in
		node_placer["strenght_out"] = strenght_out

		for out_neighbor in graph.successors(node):
			edge = graph.edges[(node,out_neighbor)]
			edge["norm_weight"] = edge["weight"]/strenght_out
			if degree_out > 1:
				alpha_ij_out = disparity_integral(edge["norm_weight"],degree_out)
				edge["alpha_out"] = alpha_ij_out
			else:
				edge["alpha_out"] = 1.0

		for in_neighbor in graph.predecessors(node):
			edge = graph.edges[(in_neighbor,node)]
			edge["norm_weight"] = edge["weight"]/strenght_in
			if degree_in > 1:
				alpha_ij_in = disparity_integral(edge["norm_weight"],degree_in)
				edge["alpha_in"] = alpha_ij_in
			else:
				edge["alpha_in"] = 1.0
	return graph


def calc_thresh(alpha,alpha_thresh):
	return alpha < alpha_thresh


def cut_graph(fgraph,alpha_thr_in,alpha_thr_out):
	#fgraph = graph.copy()
	edge_to_filter = []
	for edge in fgraph.edges():
		node_i = edge[0]
		node_j = edge[1]

		degree_i_out = fgraph.out_degree(node_i)
		degree_j_out = fgraph.out_degree(node_j)
		degree_i_in = fgraph.in_degree(node_i)
		degree_j_in = fgraph.in_degree(node_j)

		if degree_i_out == 1 & degree_i_in > 1:
			if degree_j_in > 1 & degree_j_out > 1:
				continue


		if degree_i_out == 1 & degree_j_in > 1:
			alpha_in_ji = fgraph.edges[(node_j,node_i)]["alpha_in"]
			if calc_thresh(alpha_in_ji,alpha_thr_in):
				continue
			else:
				edge_to_filter.append(edge)
				continue
		if degree_i_in == 1 & degree_j_out > 1:
			alpha_out_ji = fgraph.edges[(node_j,node_i)]["alpha_out"]
			if calc_thresh(alpha_out_ji,alpha_thr_out):
				continue
			else:
				edge_to_filter.append(edge)
				continue

		#normali
		if "alpha_in" in fgraph.edges[edge]:
			alpha_in_ij = fgraph.edges[(node_i,node_j)]["alpha_in"]
			if calc_thresh(alpha_in_ij,alpha_thr_in):
				continue
			else:
				edge_to_filter.append(edge)
		if "alpha_out" in fgraph.edges[edge]:
			alpha_out_ij = fgraph.edges[(node_i,node_j)]["alpha_out"]
			if calc_thresh(alpha_out_ij,alpha_thr_out):
				continue
			else:
				edge_to_filter.append(edge)
	#togliere
	if len(edge_to_filter) == 0:
		return fgraph
	else:
		fgraph.remove_edges_from(edge_to_filter)
		return fgraph


def filter_user_network(year_week_tuple,kind):
	year = year_week_tuple[0]
	week = year_week_tuple[1]
	year_week = str(year)+"_"+str(week)
	graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
	Ntot = graph.number_of_nodes()
	Etot = graph.number_of_edges()
	Wtot = sum([graph.edges[edge]["weight"] for edge in graph.edges()])
	alpha_for = 0.8
	graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
	graph = disparity_filter(graph)
	graph = cut_graph(graph,alpha_for,alpha_for)
	nodes_to_remove = [node for node in graph.nodes() if graph.in_degree(node) == 0 & graph.out_degree(node) == 0]
	graph.remove_nodes_from(nodes_to_remove)
	Nb = graph.number_of_nodes()
	Eb = graph.number_of_edges()
	Wb = sum([graph.edges[edge]["weight"] for edge in graph.edges()])
	#julia part
	g = graph.to_undirected()
	nodes_to_remove = [node for node in g.nodes() if g.degree(node) == 0]
	g.remove_nodes_from(nodes_to_remove)
	largest_cc = g.subgraph(max(nx.connected_components(g), key=len))
	nx.write_gpickle(largest_cc,"data/network/network_user_filter_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))


def main(kind):
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	for year_week in tqdm(year_weeks):
		filter_user_network(year_week,kind)

main("politics")