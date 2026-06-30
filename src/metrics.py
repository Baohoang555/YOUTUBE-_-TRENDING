
import json
from pathlib import Path
import networkx as nx
import pandas as pd
import powerlaw
import community as community_louvain  # package python-louvain
import numpy as np 
from collections import Counter
 
from typing import Dict, Hashable, Any
 
def compute_small_world_sigma(G: nx.Graph, n_random: int = 5, seed: int = 42) -> dict:
    largest_cc_nodes = max(nx.connected_components(G), key=len)
    G_lcc = G.subgraph(largest_cc_nodes).copy()
 
    C = nx.average_clustering(G_lcc)
    L = nx.average_shortest_path_length(G_lcc)
 
    n = G_lcc.number_of_nodes()
    m = G_lcc.number_of_edges()
 
    C_rand_list, L_rand_list = [], []
    for i in range(n_random):
        G_rand = nx.gnm_random_graph(n, m, seed=seed + i)
        if nx.is_connected(G_rand):
            G_rand_lcc = G_rand
        else:
            rand_lcc_nodes = max(nx.connected_components(G_rand), key=len)
            G_rand_lcc = G_rand.subgraph(rand_lcc_nodes).copy()
        C_rand_list.append(nx.average_clustering(G_rand_lcc))
        L_rand_list.append(nx.average_shortest_path_length(G_rand_lcc))
 
    C_rand = sum(C_rand_list) / len(C_rand_list)
    L_rand = sum(L_rand_list) / len(L_rand_list)
    sigma = (C / C_rand) / (L / L_rand)
 
    return {
        "C": C,
        "L": L,
        "C_rand": C_rand,
        "L_rand": L_rand,
        "sigma": sigma,
        "is_small_world": sigma > 1,
    }
def compute_weighted_degree(G:nx.Graph)->dict:

    weighted_degrees = dict(
        G.degree(weight="weight")
    )


    values = list(
        weighted_degrees.values()
    )


    return {

        "average_weighted_degree":
            np.mean(values),

        "max_weighted_degree":
            max(values),

        "top_weighted_nodes":
            sorted(
                weighted_degrees.items(),
                key=lambda x:x[1],
                reverse=True
            )[:10]
    }
def compute_hub_concentration(G:nx.Graph)->dict:


    degrees = sorted(
        [d for _,d in G.degree()],
        reverse=True
    )


    total_degree = sum(degrees)


    top_1_percent = max(
        1,
        int(len(degrees)*0.01)
    )


    top_share = (
        sum(degrees[:top_1_percent])
        /
        total_degree
    )


    return {

        "top_1_percent_degree_share":
            top_share
    }
def compute_kcore(G:nx.Graph)->dict:


    core = nx.core_number(G)


    values=list(
        core.values()
    )


    return {


        "max_core_number":
            max(values),


        "average_core_number":
            np.mean(values),


        "core_distribution":
            dict(
                Counter(values)
            )
    }
def compute_basic_metrics(G: nx.Graph) -> dict:

    largest_cc_nodes = max(
        nx.connected_components(G),
        key=len
    )

    G_lcc = G.subgraph(
        largest_cc_nodes
    ).copy()


    avg_degree = (
        sum(
            degree
            for _, degree in G.degree()
        )
        /
        G.number_of_nodes()
    )


    triangle_dict = dict(
    nx.triangles(G)  # type: ignore
    )


    num_triangles = (
    sum(
        int(v)
        for v in triangle_dict.values()
    )
    // 3
    )


    return {

        "num_nodes":
            G.number_of_nodes(),

        "num_edges":
            G.number_of_edges(),

        "average_degree":
            avg_degree,

        "density":
            nx.density(G),

        "average_clustering":
            nx.average_clustering(G),

        "transitivity":
            nx.transitivity(G),

        "num_triangles":
            num_triangles,

        "num_connected_components":
            nx.number_connected_components(G),

        "largest_cc_size":
            G_lcc.number_of_nodes(),

        "largest_cc_fraction":
            (
                G_lcc.number_of_nodes()
                /
                G.number_of_nodes()
            ),

        "average_shortest_path_length":
            nx.average_shortest_path_length(G_lcc),

        "diameter":
            nx.diameter(G_lcc)
    }
def compute_assortativity(G:nx.Graph)->dict:

    r = nx.degree_assortativity_coefficient(G)

    return {
        "degree_assortativity": r
    }
def compute_degree_distribution(G:nx.Graph)->dict:

    degrees = [
        d for _,d in G.degree()
    ]

    counter = Counter(degrees)

    distribution = {
        str(k):v
        for k,v in sorted(counter.items())
    }

    return {
        "min_degree":min(degrees),
        "max_degree":max(degrees),
        "mean_degree":np.mean(degrees),
        "degree_distribution":distribution
    }
    
def community_statistics(G:nx.Graph)->dict:

    result = detect_communities(G)

    partition = result["partition"]


    sizes = Counter(
        partition.values()
    )


    return {

        "num_communities":
            result["num_communities"],

        "modularity":
            result["modularity"],


        "largest_community_size":
            max(sizes.values()),


        "community_sizes":
            dict(sizes)

    }
def compute_degree_gini(G:nx.Graph)->float:


    degrees=np.array(
        [d for _,d in G.degree()]
    )


    degrees=np.sort(degrees)


    n=len(degrees)


    index=np.arange(1,n+1)


    return (
        (np.sum((2*index-n-1)*degrees))
        /
        (n*np.sum(degrees))
    )
def get_top_nodes(
        centrality_df,
        top_k=10):

    return (
        centrality_df
        .head(top_k)
        .to_dict(
            orient="records"
        )
    )
 
def fit_power_law(G: nx.Graph) -> dict:
    degrees = [d for _, d in G.degree() if d > 0]  # bỏ node degree=0 nếu có
 
    fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
    R, p = fit.distribution_compare("power_law", "exponential", normalized_ratio=True)
 
    return {
        "alpha": fit.power_law.alpha,
        "xmin": fit.power_law.xmin,
        "ks_distance": fit.power_law.D,
        "loglikelihood_ratio_vs_exponential": R,
        "p_value_vs_exponential": p,
        "favors_power_law": bool(R > 0 and p < 0.05),
    }
 
 
def compute_centrality(G: nx.Graph, approx_betweenness_above: int = 1000) -> pd.DataFrame:
    n = G.number_of_nodes()
    k = 500 if n > approx_betweenness_above else None
 
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, k=k, weight="weight", seed=42)
    pagerank = nx.pagerank(G, weight="weight")
 
    df = pd.DataFrame({"channel": list(G.nodes())})
    df["degree_centrality"] = df["channel"].map(degree_centrality)
    df["betweenness_centrality"] = df["channel"].map(betweenness_centrality)
    df["pagerank"] = df["channel"].map(pagerank)
 
    return df.sort_values("pagerank", ascending=False).reset_index(drop=True)
 
 
def detect_communities(G: nx.Graph, seed: int = 42) -> dict:
    partition = community_louvain.best_partition(G, weight="weight", random_state=seed)
    modularity = community_louvain.modularity(partition, G, weight="weight")
 
    return {
        "partition": partition,
        "modularity": modularity,
        "num_communities": len(set(partition.values())),
    }
 
 
def save_metrics_json(metrics: dict, country: str, output_dir: Path, filename: str) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{country}_{filename}"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)
    return out_path
 
 
def save_centrality_csv(df: pd.DataFrame, country: str, output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{country}_centrality.csv"
    df.to_csv(out_path, index=False)
    return out_path
 
def run_all_metrics(G):

    result={}


    result.update(
        compute_basic_metrics(G)
    )


    result.update(
        compute_small_world_sigma(G)
    )


    result.update(
        compute_assortativity(G)
    )


    result.update(
        compute_degree_distribution(G)
    )


    result.update(
        compute_weighted_degree(G)
    )


    result.update(
        compute_hub_concentration(G)
    )


    result.update(
        compute_kcore(G)
    )


    result.update(
        fit_power_law(G)
    )


    comm=community_statistics(G)

    result.update(comm)


    result["degree_gini"] = compute_degree_gini(G)


    return result
if __name__ == "__main__":
    try:
        from loader import load_and_clean
        from graph_builder import build_graph
    except ImportError:
        from src.loader import load_and_clean
        from src.graph_builder import build_graph
 
    try:
        df_us = load_and_clean("US")
        G_us = build_graph(df_us, weight_threshold=1)
 
        print("Basic metrics:", compute_basic_metrics(G_us))
        print("Power-law fit:", fit_power_law(G_us))
 
        centrality_df = compute_centrality(G_us)
        print(centrality_df.head())
 
        comm = detect_communities(G_us)
        print(f"Số cộng đồng: {comm['num_communities']}, modularity: {comm['modularity']:.4f}")
    except Exception as e:
        print(f"Lỗi khi chạy thử nghiệm: {e}")
 