"""
community_detector.py
=======================
Deteksi komunitas vendor mencurigakan dalam knowledge graph.

Algoritma:
1. Louvain — mendeteksi komunitas densely connected
2. Weakly Connected Components — menemukan cluster terisolasi
3. PageRank — identifikasi vendor paling "berpengaruh"
4. Degree centrality — node dengan koneksi terbanyak
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    LOUVAIN_RESOLUTION,
    ML_OUTPUT_DIR,
)


def _try_louvain(G: nx.Graph, resolution: float = LOUVAIN_RESOLUTION) -> dict:
    """
    Run Louvain community detection. 
    Falls back to greedy modularity if community package not available.
    """
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G, resolution=resolution)
        return partition
    except ImportError:
        # Fallback: greedy modularity communities
        communities = nx.community.greedy_modularity_communities(G)
        partition = {}
        for i, comm in enumerate(communities):
            for node in comm:
                partition[node] = i
        return partition


def detect_communities(G: nx.Graph) -> dict:
    """
    Deteksi komunitas dalam graph menggunakan Louvain.

    Returns
    -------
    dict
        Mapping node_id → community_id.
    """
    # Hanya proses pada connected subgraph yang cukup besar
    partition = _try_louvain(G)
    return partition


def compute_pagerank(G: nx.Graph, alpha: float = 0.85) -> dict:
    """
    Hitung PageRank untuk setiap node.
    Node dengan PageRank tinggi = "berpengaruh" dalam jaringan.

    Returns
    -------
    dict
        Mapping node_id → pagerank score.
    """
    return nx.pagerank(G, alpha=alpha)


def compute_centrality_metrics(G: nx.Graph) -> pd.DataFrame:
    """
    Hitung berbagai centrality metrics untuk setiap node.

    Returns
    -------
    pd.DataFrame
        DataFrame dengan degree, betweenness, closeness centrality.
    """
    metrics = []

    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    pagerank = compute_pagerank(G)

    # Closeness hanya untuk connected components
    closeness_cent = {}
    for component in nx.connected_components(G):
        subgraph = G.subgraph(component)
        if len(subgraph) > 1:
            cc = nx.closeness_centrality(subgraph)
            closeness_cent.update(cc)

    for node in G.nodes():
        data = G.nodes[node]
        metrics.append({
            "node_id": node,
            "node_type": data.get("node_type", "Unknown"),
            "degree": G.degree(node),
            "degree_centrality": round(degree_cent.get(node, 0), 6),
            "betweenness_centrality": round(betweenness_cent.get(node, 0), 6),
            "closeness_centrality": round(closeness_cent.get(node, 0), 6),
            "pagerank": round(pagerank.get(node, 0), 6),
        })

    return pd.DataFrame(metrics)


def find_connected_components(G: nx.Graph) -> list[set]:
    """
    Temukan semua connected components dan return yang berisi > 1 vendor.

    Returns
    -------
    list[set]
        List of sets, each containing node IDs in a component.
    """
    components = list(nx.connected_components(G))

    # Filter: hanya komponen dengan > 1 vendor node
    vendor_components = []
    for comp in components:
        vendor_count = sum(1 for n in comp if G.nodes[n].get("node_type") == "Vendor")
        if vendor_count > 1:
            vendor_components.append(comp)

    return vendor_components


def run_community_detection(
    G: nx.Graph,
    save: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """
    Jalankan full community detection pipeline.

    Returns
    -------
    tuple
        (centrality_df, communities_dict)
    """
    print("\n" + "=" * 60)
    print("COMMUNITY DETECTION & GRAPH METRICS")
    print("=" * 60)

    # 1. Connected components
    print("\n--- Connected Components ---")
    components = list(nx.connected_components(G))
    print(f"  Total components: {len(components)}")
    vendor_comps = find_connected_components(G)
    print(f"  Components with >1 vendor: {len(vendor_comps)}")
    if vendor_comps:
        sizes = [len(c) for c in vendor_comps]
        print(f"  Largest multi-vendor component: {max(sizes)} nodes")

    # 2. Community detection (Louvain)
    print("\n--- Louvain Community Detection ---")
    communities = detect_communities(G)
    n_communities = len(set(communities.values()))
    print(f"  Communities found: {n_communities}")

    # Community size distribution
    comm_sizes = pd.Series(communities).value_counts()
    print(f"  Largest community : {comm_sizes.max()} nodes")
    print(f"  Smallest community: {comm_sizes.min()} nodes")
    print(f"  Average size      : {comm_sizes.mean():.1f} nodes")

    # 3. Centrality metrics
    print("\n--- Centrality Metrics ---")
    centrality_df = compute_centrality_metrics(G)

    # Add community labels
    centrality_df["community_id"] = centrality_df["node_id"].map(communities).fillna(-1).astype(int)

    # Top vendors by PageRank
    vendor_centrality = centrality_df[centrality_df["node_type"] == "Vendor"]
    if not vendor_centrality.empty:
        top_vendors = vendor_centrality.nlargest(10, "pagerank")
        print(f"\n  Top 10 Vendors by PageRank:")
        for _, row in top_vendors.iterrows():
            print(f"    {row['node_id']:12s} | degree={row['degree']:3d} | "
                  f"pagerank={row['pagerank']:.6f} | community={row['community_id']}")

    # Suspicious: high centrality vendors (potential intermediaries)
    if not vendor_centrality.empty:
        high_betweenness = vendor_centrality[
            vendor_centrality["betweenness_centrality"] > vendor_centrality["betweenness_centrality"].quantile(0.95)
        ]
        print(f"\n  Vendors with high betweenness (potential intermediaries): {len(high_betweenness)}")

    if save:
        centrality_df.to_csv(ML_OUTPUT_DIR / "graph_centrality.csv", index=False)
        print(f"\n  Saved → {ML_OUTPUT_DIR / 'graph_centrality.csv'}")

    return centrality_df, communities


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
    from ml_engine.data_generator.generate_vendor_network import generate_vendor_network
    from ml_engine.graph_analysis.neo4j_loader import build_graph

    df_trx = generate_apbd_data(save=False)
    df_vendor = generate_vendor_network(save=False)
    G = build_graph(df_trx, df_vendor)

    centrality_df, communities = run_community_detection(G)
