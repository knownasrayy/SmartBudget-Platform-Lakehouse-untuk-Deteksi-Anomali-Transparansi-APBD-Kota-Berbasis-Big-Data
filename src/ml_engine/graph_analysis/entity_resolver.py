"""
entity_resolver.py
=====================
Entity Resolution — mendeteksi vendor yang sebenarnya satu entitas
meskipun terdaftar dengan nama berbeda.

Metode:
1. Fuzzy string matching pada nama vendor
2. Exact match pada alamat dan NPWP
3. Shared director detection
4. Output: cluster ID per vendor group
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    FUZZY_MATCH_THRESHOLD,
    ML_OUTPUT_DIR,
)


def _simple_similarity(s1: str, s2: str) -> float:
    """
    Hitung similaritas string sederhana (character-based).
    Menghindari dependency pada fuzzywuzzy jika belum terinstall.
    Menggunakan metode Dice coefficient pada bigrams.
    """
    if not s1 or not s2:
        return 0.0

    s1 = s1.lower().strip()
    s2 = s2.lower().strip()

    if s1 == s2:
        return 100.0

    # Generate bigrams
    def bigrams(s):
        return set(s[i:i+2] for i in range(len(s) - 1))

    bg1 = bigrams(s1)
    bg2 = bigrams(s2)

    if not bg1 or not bg2:
        return 0.0

    intersection = len(bg1 & bg2)
    dice = (2.0 * intersection) / (len(bg1) + len(bg2))

    return dice * 100


def _get_similarity_func():
    """Try to import fuzzywuzzy, fallback to simple similarity."""
    try:
        from fuzzywuzzy import fuzz
        return fuzz.ratio
    except ImportError:
        return _simple_similarity


def find_shared_addresses(df_vendors: pd.DataFrame) -> pd.DataFrame:
    """
    Temukan vendor-vendor yang berbagi alamat yang sama.

    Returns
    -------
    pd.DataFrame
        Pairs of vendors dengan alamat sama.
    """
    # Group vendors by alamat
    address_groups = df_vendors.groupby("alamat")["id_vendor"].apply(list).reset_index()
    address_groups = address_groups[address_groups["id_vendor"].apply(len) > 1]

    pairs = []
    for _, row in address_groups.iterrows():
        vendors = row["id_vendor"]
        for v1, v2 in combinations(vendors, 2):
            pairs.append({
                "vendor_1": v1,
                "vendor_2": v2,
                "match_type": "shared_address",
                "shared_value": row["alamat"],
                "confidence": 100.0,
            })

    return pd.DataFrame(pairs)


def find_shared_directors(df_vendors: pd.DataFrame) -> pd.DataFrame:
    """
    Temukan vendor-vendor yang dikelola oleh direktur yang sama.

    Returns
    -------
    pd.DataFrame
        Pairs of vendors dengan direktur sama.
    """
    director_groups = df_vendors.groupby("nama_direktur")["id_vendor"].apply(list).reset_index()
    director_groups = director_groups[director_groups["id_vendor"].apply(len) > 1]

    pairs = []
    for _, row in director_groups.iterrows():
        vendors = row["id_vendor"]
        for v1, v2 in combinations(vendors, 2):
            pairs.append({
                "vendor_1": v1,
                "vendor_2": v2,
                "match_type": "shared_director",
                "shared_value": row["nama_direktur"],
                "confidence": 100.0,
            })

    return pd.DataFrame(pairs)


def find_similar_names(
    df_vendors: pd.DataFrame,
    threshold: float = FUZZY_MATCH_THRESHOLD,
) -> pd.DataFrame:
    """
    Temukan vendor-vendor dengan nama serupa (kemungkinan duplikat).

    Returns
    -------
    pd.DataFrame
        Pairs of vendors dengan nama mirip.
    """
    similarity_func = _get_similarity_func()
    vendors = df_vendors[["id_vendor", "nama_vendor"]].values.tolist()

    pairs = []
    n = len(vendors)

    # Optimization: hanya cek pasangan yang punya kata depan sama (PT/CV)
    for i in range(n):
        for j in range(i + 1, min(i + 50, n)):  # Limit comparisons
            v1_id, v1_name = vendors[i]
            v2_id, v2_name = vendors[j]

            # Quick filter: harus punya prefix sama
            if v1_name[:2] != v2_name[:2]:
                continue

            score = similarity_func(v1_name, v2_name)
            if score >= threshold:
                pairs.append({
                    "vendor_1": v1_id,
                    "vendor_2": v2_id,
                    "match_type": "similar_name",
                    "shared_value": f"{v1_name} ↔ {v2_name}",
                    "confidence": round(score, 1),
                })

    return pd.DataFrame(pairs)


def build_entity_clusters(
    all_pairs: pd.DataFrame,
    df_vendors: pd.DataFrame,
) -> pd.DataFrame:
    """
    Bangun cluster ID dari semua pasangan vendor yang terhubung.
    Menggunakan Union-Find (Disjoint Set Union).

    Returns
    -------
    pd.DataFrame
        df_vendors + kolom entity_cluster_id.
    """
    if all_pairs.empty:
        df_vendors = df_vendors.copy()
        df_vendors["entity_cluster_id"] = range(len(df_vendors))
        df_vendors["is_in_cluster"] = False
        return df_vendors

    # Union-Find
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Process all pairs
    for _, row in all_pairs.iterrows():
        union(row["vendor_1"], row["vendor_2"])

    # Assign cluster IDs
    clusters = defaultdict(list)
    all_vendor_ids = set(df_vendors["id_vendor"])
    for vid in all_vendor_ids:
        root = find(vid) if vid in parent else vid
        clusters[root].append(vid)

    # Map vendor → cluster
    vendor_cluster = {}
    cluster_id = 0
    for root, members in clusters.items():
        for vid in members:
            vendor_cluster[vid] = cluster_id
        cluster_id += 1

    # Assign remaining vendors without pairs
    for vid in all_vendor_ids:
        if vid not in vendor_cluster:
            vendor_cluster[vid] = cluster_id
            cluster_id += 1

    df_vendors = df_vendors.copy()
    df_vendors["entity_cluster_id"] = df_vendors["id_vendor"].map(vendor_cluster)

    # Mark vendors that are in a multi-vendor cluster
    cluster_sizes = df_vendors["entity_cluster_id"].value_counts()
    multi_clusters = set(cluster_sizes[cluster_sizes > 1].index)
    df_vendors["is_in_cluster"] = df_vendors["entity_cluster_id"].isin(multi_clusters)

    return df_vendors


def run_entity_resolution(
    df_vendors: pd.DataFrame,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Jalankan full entity resolution pipeline.

    Returns
    -------
    tuple
        (df_vendors_with_clusters, all_pairs)
    """
    print("\n" + "=" * 60)
    print("ENTITY RESOLUTION")
    print("=" * 60)

    # 1. Shared addresses
    print("\n--- Shared Address Detection ---")
    pairs_addr = find_shared_addresses(df_vendors)
    print(f"  Found {len(pairs_addr)} vendor pairs with shared addresses")

    # 2. Shared directors
    print("\n--- Shared Director Detection ---")
    pairs_dir = find_shared_directors(df_vendors)
    print(f"  Found {len(pairs_dir)} vendor pairs with shared directors")

    # 3. Similar names
    print("\n--- Similar Name Detection ---")
    pairs_name = find_similar_names(df_vendors)
    print(f"  Found {len(pairs_name)} vendor pairs with similar names")

    # Combine all pairs
    all_pairs = pd.concat([pairs_addr, pairs_dir, pairs_name], ignore_index=True)
    all_pairs = all_pairs.drop_duplicates(subset=["vendor_1", "vendor_2"])
    print(f"\n  Total unique pairs: {len(all_pairs)}")

    # Build clusters
    print("\n--- Building Entity Clusters ---")
    df_vendors = build_entity_clusters(all_pairs, df_vendors)

    n_clusters = df_vendors["entity_cluster_id"].nunique()
    n_multi = df_vendors["is_in_cluster"].sum()
    print(f"  Total clusters      : {n_clusters}")
    print(f"  Multi-vendor clusters: {df_vendors[df_vendors['is_in_cluster']]['entity_cluster_id'].nunique()}")
    print(f"  Vendors in clusters : {n_multi}")

    if save:
        all_pairs.to_csv(ML_OUTPUT_DIR / "entity_pairs.csv", index=False)
        df_vendors.to_csv(ML_OUTPUT_DIR / "vendor_clusters.csv", index=False)
        print(f"  Saved → {ML_OUTPUT_DIR}")

    return df_vendors, all_pairs


if __name__ == "__main__":
    from ml_engine.data_generator.generate_vendor_network import generate_vendor_network

    df_vendor = generate_vendor_network(save=False)
    df_clustered, pairs = run_entity_resolution(df_vendor)

    print("\n--- Sample Clusters (multi-vendor) ---")
    multi = df_clustered[df_clustered["is_in_cluster"]]
    if not multi.empty:
        for cid in multi["entity_cluster_id"].unique()[:5]:
            cluster = multi[multi["entity_cluster_id"] == cid]
            print(f"\n  Cluster {cid}:")
            for _, v in cluster.iterrows():
                print(f"    {v['id_vendor']}: {v['nama_vendor']} | {v['alamat'][:50]}... | Dir: {v['nama_direktur']}")
