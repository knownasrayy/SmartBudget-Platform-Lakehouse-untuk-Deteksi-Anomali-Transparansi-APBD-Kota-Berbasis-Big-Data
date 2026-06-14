"""
visualize.py
==============
Modul visualisasi untuk validasi dan presentasi hasil ML Engine.

Visualisasi:
1. Benford distribution plot
2. Anomaly scatter plot (PCA 2D)
3. Risk heatmap per SKPD × kota
4. Graph network visualization
5. Ensemble score distribution
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_engine.config import (
    PLOTS_DIR,
    COLOR_PALETTE,
    PLOT_DPI,
    PLOT_FIGSIZE,
)

# Benford expected distribution
BENFORD_EXPECTED = {d: np.log10(1 + 1 / d) for d in range(1, 10)}


def plot_benford_distribution(
    df: pd.DataFrame,
    value_column: str = "realisasi",
    title: str = "Benford's Law Analysis — Distribusi Digit Pertama Belanja APBD",
    save_name: str = "benford_distribution.png",
) -> str:
    """Plot perbandingan distribusi digit pertama vs Benford teoritis."""
    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

    # Extract first digits
    values = df[value_column].dropna()
    values = values[values > 0]
    first_digits = values.apply(lambda x: int(str(int(x))[0]))
    observed = first_digits.value_counts(normalize=True).sort_index()

    digits = range(1, 10)
    expected = [BENFORD_EXPECTED[d] for d in digits]
    observed_vals = [observed.get(d, 0) for d in digits]

    x = np.arange(len(digits))
    width = 0.35

    bars_expected = ax.bar(x - width/2, expected, width, label="Benford Teoritis",
                           color=COLOR_PALETTE["primary"], alpha=0.8, edgecolor="white")
    bars_observed = ax.bar(x + width/2, observed_vals, width, label="Observasi Data",
                           color=COLOR_PALETTE["anomaly"], alpha=0.8, edgecolor="white")

    ax.set_xlabel("Digit Pertama", fontsize=12)
    ax.set_ylabel("Proporsi", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(digits)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    # Annotate significant deviations
    for i, d in enumerate(digits):
        diff = observed_vals[i] - expected[i]
        if abs(diff) > 0.02:
            color = COLOR_PALETTE["anomaly"] if diff > 0 else COLOR_PALETTE["normal"]
            ax.annotate(f"{diff:+.1%}", xy=(x[i] + width/2, observed_vals[i]),
                       ha="center", va="bottom", fontsize=9, color=color, fontweight="bold")

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def plot_anomaly_scatter(
    df: pd.DataFrame,
    save_name: str = "anomaly_scatter_pca.png",
) -> str:
    """Plot anomaly scatter menggunakan PCA 2D projection."""
    from sklearn.decomposition import PCA

    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

    # Select numeric features for PCA
    feature_cols = [
        "log_realisasi", "log_pagu", "rasio_realisasi_pagu",
        "zscore_per_skpd", "zscore_per_rekening",
        "is_q4", "trailing_zeros_realisasi",
    ]
    available = [c for c in feature_cols if c in df.columns]

    if len(available) < 2:
        print("  ⚠️  Not enough features for PCA scatter plot")
        plt.close(fig)
        return ""

    X = df[available].fillna(0).values

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # Color by risk category
    if "risk_category" in df.columns:
        colors = {
            "LOW": COLOR_PALETTE["normal"],
            "MEDIUM": COLOR_PALETTE["warning"],
            "HIGH": "#e67e22",
            "CRITICAL": COLOR_PALETTE["anomaly"],
        }
        for cat, color in colors.items():
            mask = df["risk_category"] == cat
            if mask.any():
                ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                          c=color, label=cat, alpha=0.6, s=20, edgecolors="white", linewidth=0.3)
    elif "is_flagged" in df.columns:
        normal_mask = ~df["is_flagged"]
        anomaly_mask = df["is_flagged"]
        ax.scatter(X_pca[normal_mask, 0], X_pca[normal_mask, 1],
                  c=COLOR_PALETTE["normal"], label="Normal", alpha=0.4, s=15)
        ax.scatter(X_pca[anomaly_mask, 0], X_pca[anomaly_mask, 1],
                  c=COLOR_PALETTE["anomaly"], label="Anomali", alpha=0.8, s=30, edgecolors="black", linewidth=0.5)

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)", fontsize=12)
    ax.set_title("Anomaly Detection — PCA 2D Projection", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(alpha=0.2)

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def plot_risk_heatmap(
    df: pd.DataFrame,
    save_name: str = "risk_heatmap_skpd_kota.png",
) -> str:
    """Plot heatmap risk score per SKPD × kota."""
    fig, ax = plt.subplots(figsize=(14, 10))

    if "ensemble_score" not in df.columns:
        print("  ⚠️  ensemble_score not available for heatmap")
        plt.close(fig)
        return ""

    # Pivot table
    pivot = df.pivot_table(
        values="ensemble_score",
        index="nama_skpd",
        columns="kota",
        aggfunc="mean",
    ).fillna(0)

    # Sort by average risk
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)

    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            color = "white" if val > 40 else "black"
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=7, color=color)

    ax.set_title("Risk Score Heatmap — SKPD × Kota", fontsize=14, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Average Risk Score", shrink=0.8)

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def plot_ensemble_distribution(
    df: pd.DataFrame,
    save_name: str = "ensemble_score_distribution.png",
) -> str:
    """Plot distribusi ensemble risk score."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    if "ensemble_score" not in df.columns:
        print("  ⚠️  ensemble_score not available")
        plt.close(fig)
        return ""

    # Left: Histogram
    ax1 = axes[0]
    ax1.hist(df["ensemble_score"], bins=50, color=COLOR_PALETTE["primary"],
             alpha=0.7, edgecolor="white")
    ax1.axvline(25, color=COLOR_PALETTE["warning"], linestyle="--", label="Medium threshold")
    ax1.axvline(50, color="#e67e22", linestyle="--", label="High threshold")
    ax1.axvline(75, color=COLOR_PALETTE["anomaly"], linestyle="--", label="Critical threshold")
    ax1.set_xlabel("Ensemble Risk Score", fontsize=12)
    ax1.set_ylabel("Jumlah Transaksi", fontsize=12)
    ax1.set_title("Distribusi Risk Score", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(axis="y", alpha=0.3)

    # Right: Risk category pie chart
    ax2 = axes[1]
    if "risk_category" in df.columns:
        risk_counts = df["risk_category"].value_counts()
        colors_map = {
            "LOW": COLOR_PALETTE["normal"],
            "MEDIUM": COLOR_PALETTE["warning"],
            "HIGH": "#e67e22",
            "CRITICAL": COLOR_PALETTE["anomaly"],
        }
        cats = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        sizes = [risk_counts.get(c, 0) for c in cats]
        colors = [colors_map[c] for c in cats]
        labels = [f"{c}\n({s})" for c, s in zip(cats, sizes)]

        wedges, texts, autotexts = ax2.pie(
            sizes, labels=labels, colors=colors,
            autopct="%1.1f%%", startangle=90,
            textprops={"fontsize": 10},
        )
        ax2.set_title("Distribusi Risk Category", fontsize=13, fontweight="bold")

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def plot_vendor_network(
    G,
    centrality_df: Optional[pd.DataFrame] = None,
    max_nodes: int = 100,
    save_name: str = "vendor_network_graph.png",
) -> str:
    """Plot network graph dari vendor relationships."""
    import networkx as nx

    fig, ax = plt.subplots(figsize=(16, 12))

    # Filter to vendor nodes & their connections (limit for readability)
    vendor_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Vendor"]

    if len(vendor_nodes) > max_nodes:
        # Keep most connected vendors
        degrees = {n: G.degree(n) for n in vendor_nodes}
        vendor_nodes = sorted(degrees, key=degrees.get, reverse=True)[:max_nodes]

    # Get subgraph
    related_nodes = set(vendor_nodes)
    for v in vendor_nodes:
        for neighbor in G.neighbors(v):
            related_nodes.add(neighbor)

    if len(related_nodes) > max_nodes * 3:
        related_nodes = set(vendor_nodes)  # Only vendor nodes
        for v in list(vendor_nodes)[:50]:
            for neighbor in G.neighbors(v):
                related_nodes.add(neighbor)

    subG = G.subgraph(related_nodes)

    # Node colors by type
    node_colors = []
    node_sizes = []
    for node in subG.nodes():
        ntype = subG.nodes[node].get("node_type", "Unknown")
        if ntype == "Vendor":
            node_colors.append(COLOR_PALETTE["primary"])
            node_sizes.append(80)
        elif ntype == "Direktur":
            node_colors.append(COLOR_PALETTE["secondary"])
            node_sizes.append(40)
        elif ntype == "Alamat":
            node_colors.append(COLOR_PALETTE["warning"])
            node_sizes.append(40)
        elif ntype == "SKPD":
            node_colors.append(COLOR_PALETTE["normal"])
            node_sizes.append(60)
        else:
            node_colors.append("#95a5a6")
            node_sizes.append(30)

    # Layout
    try:
        pos = nx.spring_layout(subG, k=2, iterations=50, seed=42)
    except Exception:
        pos = nx.random_layout(subG, seed=42)

    nx.draw_networkx_edges(subG, pos, ax=ax, alpha=0.2, width=0.5)
    nx.draw_networkx_nodes(subG, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.8, edgecolors="white", linewidths=0.5)

    # Legend
    legend_patches = [
        mpatches.Patch(color=COLOR_PALETTE["primary"], label="Vendor"),
        mpatches.Patch(color=COLOR_PALETTE["secondary"], label="Direktur"),
        mpatches.Patch(color=COLOR_PALETTE["warning"], label="Alamat"),
        mpatches.Patch(color=COLOR_PALETTE["normal"], label="SKPD"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=10)

    ax.set_title("Vendor Relationship Network Graph", fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def plot_benford_by_skpd(
    benford_results: pd.DataFrame,
    save_name: str = "benford_skpd_deviation.png",
) -> str:
    """Plot MAD (Mean Absolute Deviation) per SKPD dari Benford."""
    fig, ax = plt.subplots(figsize=(12, 8))

    if benford_results.empty or "mad" not in benford_results.columns:
        print("  ⚠️  No Benford results to plot")
        plt.close(fig)
        return ""

    data = benford_results[benford_results["status"] == "ANALYZED"].copy()
    data = data.sort_values("mad", ascending=True).tail(20)  # Top 20

    colors = [COLOR_PALETTE["anomaly"] if s else COLOR_PALETTE["normal"]
              for s in data["is_suspicious"]]

    bars = ax.barh(range(len(data)), data["mad"], color=colors, alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data["group_value"], fontsize=9)
    ax.set_xlabel("Mean Absolute Deviation (MAD)", fontsize=12)
    ax.set_title("Benford's Law Deviation per SKPD\n(Higher = More Suspicious)", fontsize=13, fontweight="bold")
    ax.axvline(0.015, color=COLOR_PALETTE["warning"], linestyle="--", alpha=0.7, label="Threshold")

    legend_patches = [
        mpatches.Patch(color=COLOR_PALETTE["anomaly"], label="Suspicious (p < 0.05)"),
        mpatches.Patch(color=COLOR_PALETTE["normal"], label="Conforming"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=10)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = PLOTS_DIR / save_name
    fig.savefig(path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Saved → {path}")
    return str(path)


def generate_all_visualizations(
    df_transactions: pd.DataFrame,
    df_vendors: pd.DataFrame,
    benford_results: pd.DataFrame,
    G=None,
    centrality_df: Optional[pd.DataFrame] = None,
) -> list[str]:
    """Generate semua visualisasi."""
    print("\n  Generating all visualizations...")

    paths = []
    paths.append(plot_benford_distribution(df_transactions))
    paths.append(plot_anomaly_scatter(df_transactions))
    paths.append(plot_risk_heatmap(df_transactions))
    paths.append(plot_ensemble_distribution(df_transactions))
    paths.append(plot_benford_by_skpd(benford_results))

    if G is not None:
        paths.append(plot_vendor_network(G, centrality_df))

    print(f"\n  ✅ {len([p for p in paths if p])} visualizations generated in {PLOTS_DIR}")

    return [p for p in paths if p]


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data

    df = generate_apbd_data(save=False)
    plot_benford_distribution(df)
    print("  Done!")
