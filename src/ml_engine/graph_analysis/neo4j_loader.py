"""
neo4j_loader.py
=================
Konstruksi knowledge graph dari data vendor-kontrak-SKPD.

Menggunakan NetworkX untuk development (tanpa perlu Neo4j server),
dengan opsi migrasi ke Neo4j saat deployment.

Graph Schema:
- Node types: Vendor, SKPD, Kontrak, Direktur, Alamat
- Edge types: MENERIMA, MEMBERIKAN, DIMILIKI_OLEH, BERALAMAT_DI
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import ML_OUTPUT_DIR


def build_graph(
    df_transactions: pd.DataFrame,
    df_vendors: pd.DataFrame,
) -> nx.Graph:
    """
    Bangun knowledge graph dari data transaksi dan vendor.

    Parameters
    ----------
    df_transactions : pd.DataFrame
        Data transaksi APBD (silver_apbd_belanja).
    df_vendors : pd.DataFrame
        Data vendor network (silver_vendor_network).

    Returns
    -------
    nx.Graph
        Knowledge graph dengan node dan edge types.
    """
    G = nx.Graph()

    print("\n  Building knowledge graph...")

    # ---- Add Vendor nodes ----
    for _, row in df_vendors.iterrows():
        G.add_node(
            row["id_vendor"],
            node_type="Vendor",
            nama=row["nama_vendor"],
            npwp=row.get("npwp", ""),
            tahun_berdiri=row.get("tahun_berdiri", 0),
            total_kontrak=row.get("total_kontrak", 0),
            total_nilai_kontrak=row.get("total_nilai_kontrak", 0),
        )

    # ---- Add Direktur nodes & edges ----
    direktur_map = {}
    for _, row in df_vendors.iterrows():
        dir_name = row.get("nama_direktur", "Unknown")
        dir_node = f"DIR_{dir_name.replace(' ', '_')}"

        if dir_node not in direktur_map:
            G.add_node(dir_node, node_type="Direktur", nama=dir_name)
            direktur_map[dir_node] = dir_name

        G.add_edge(row["id_vendor"], dir_node, edge_type="DIMILIKI_OLEH")

    # ---- Add Alamat nodes & edges ----
    alamat_map = {}
    for _, row in df_vendors.iterrows():
        alamat = row.get("alamat", "Unknown")
        alamat_node = f"ADDR_{hash(alamat) % 100000:05d}"

        if alamat_node not in alamat_map:
            G.add_node(alamat_node, node_type="Alamat", alamat=alamat)
            alamat_map[alamat_node] = alamat

        G.add_edge(row["id_vendor"], alamat_node, edge_type="BERALAMAT_DI")

    # ---- Add SKPD nodes ----
    skpd_set = set()
    for _, row in df_transactions.iterrows():
        skpd_key = f"SKPD_{row['kode_skpd']}"
        if skpd_key not in skpd_set:
            G.add_node(
                skpd_key,
                node_type="SKPD",
                kode=row["kode_skpd"],
                nama=row["nama_skpd"],
                kota=row["kota"],
            )
            skpd_set.add(skpd_key)

    # ---- Add Kontrak edges (Vendor --MENERIMA--> transaction <--MEMBERIKAN-- SKPD) ----
    for _, row in df_transactions.iterrows():
        vendor_id = row["id_vendor"]
        skpd_key = f"SKPD_{row['kode_skpd']}"

        # Vendor-SKPD direct relationship
        if G.has_node(vendor_id) and G.has_node(skpd_key):
            if G.has_edge(vendor_id, skpd_key):
                # Increment contract count
                G[vendor_id][skpd_key]["n_contracts"] = G[vendor_id][skpd_key].get("n_contracts", 0) + 1
                G[vendor_id][skpd_key]["total_value"] = G[vendor_id][skpd_key].get("total_value", 0) + row["realisasi"]
            else:
                G.add_edge(
                    vendor_id, skpd_key,
                    edge_type="KONTRAK_DENGAN",
                    n_contracts=1,
                    total_value=row["realisasi"],
                )

    # Print summary
    n_vendors = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "Vendor")
    n_direktur = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "Direktur")
    n_alamat = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "Alamat")
    n_skpd = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "SKPD")

    print(f"  Graph constructed:")
    print(f"    Nodes: {G.number_of_nodes()} total")
    print(f"      - Vendors  : {n_vendors}")
    print(f"      - Direktur : {n_direktur}")
    print(f"      - Alamat   : {n_alamat}")
    print(f"      - SKPD     : {n_skpd}")
    print(f"    Edges: {G.number_of_edges()} total")

    return G


def get_vendor_subgraph(G: nx.Graph) -> nx.Graph:
    """
    Ekstrak subgraph hanya berisi vendor dan relasi antaranya
    (melalui shared direktur/alamat).
    """
    vendor_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Vendor"]
    return G.subgraph(vendor_nodes).copy()


def export_graph_to_cypher(G: nx.Graph, output_path: Optional[str] = None) -> str:
    """
    Export graph ke Cypher queries untuk import ke Neo4j.
    Berguna untuk migrasi ke Neo4j saat deployment.

    Returns
    -------
    str
        Cypher CREATE statements.
    """
    cypher_lines = []

    # Create nodes
    for node_id, data in G.nodes(data=True):
        node_type = data.get("node_type", "Unknown")
        props = {k: v for k, v in data.items() if k != "node_type"}
        props_str = ", ".join([f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}"
                               for k, v in props.items()])
        safe_id = str(node_id).replace("-", "_").replace(" ", "_")
        cypher_lines.append(f'CREATE ({safe_id}:{node_type} {{{props_str}}})')

    # Create relationships
    for u, v, data in G.edges(data=True):
        edge_type = data.get("edge_type", "RELATED_TO")
        safe_u = str(u).replace("-", "_").replace(" ", "_")
        safe_v = str(v).replace("-", "_").replace(" ", "_")
        cypher_lines.append(f'CREATE ({safe_u})-[:{edge_type}]->({safe_v})')

    cypher_str = ";\n".join(cypher_lines) + ";"

    if output_path:
        with open(output_path, "w") as f:
            f.write(cypher_str)
        print(f"  Cypher exported → {output_path}")

    return cypher_str


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
    from ml_engine.data_generator.generate_vendor_network import generate_vendor_network

    df_trx = generate_apbd_data(save=False)
    df_vendor = generate_vendor_network(save=False)

    G = build_graph(df_trx, df_vendor)

    print(f"\n  Density: {nx.density(G):.6f}")
    print(f"  Connected components: {nx.number_connected_components(G)}")
