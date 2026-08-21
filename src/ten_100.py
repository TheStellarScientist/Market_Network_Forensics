'''
Howdy! 

The purpose of this script is to investigate the data I'm
importing from yfinance. We'll be using the Nasdaq-100 as
the starting population. 

Question: 
Does an AI-related ecosystem emerge from the return network
without us explicitly telling the algorithm what an
"AI Company" is?

We're essentially doing some Forensic Network Science. 

This was run with: /gpfs/home/guwechue/miniconda3/bin/python src/ten_100.py > outputs/ten_100_output.txt

Well Wishes,
Demi
'''

import yfinance as yf
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Market Network Investigation!")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# Make sure figure directory exists
os.makedirs("figures", exist_ok=True)

# Validation before we begin

with open("data/nasdaq100_2025.txt", "r") as file:
    nasdaq_100_tickers = [
        line.strip()
        for line in file
        if line.strip()
    ]

# print("\nNasdaq-100 Population Check")
# print("___________________________")

# print("Number of ticker symbols:")
# print(len(nasdaq_100_tickers))

# print("\nFirst 10:")
# print(nasdaq_100_tickers[:10])

# print("\nLast 10:")
# print(nasdaq_100_tickers[-10:])

full_data = yf.download(
    nasdaq_100_tickers,
    start="2016-01-01",
    end="2026-01-01"
)

full_close_prices = full_data["Close"]

print("\nFull Population Inspection")
print("__________________________")

print("\nClose Price Shape:")
print(full_close_prices.shape)

print("\nMissing Values Per Ticker:")
print(
    full_close_prices
    .isna()
    .sum()
    .sort_values(ascending=False)
)

missing_counts = full_close_prices.isna().sum()

tickers_with_missing_data = missing_counts[
    missing_counts > 0
]

print("\nTickers With Missing Data:")
print(tickers_with_missing_data)
# ANSS which was delisted July 2025 after being acquired by Snyopsys.


usable_tickers = [
    ticker
    for ticker in nasdaq_100_tickers
    if missing_counts[ticker] < len(full_close_prices)
]

print("\nUsable Tickers:")
print(len(usable_tickers))

# Checking the redundancy of GOOG and GOOGL
full_close_prices = full_close_prices[usable_tickers]

full_daily_returns = (
    full_close_prices
    .pct_change(fill_method=None)
)

# alphabet_correlation = full_daily_returns["GOOG"].corr(
#     full_daily_returns["GOOGL"]
# )

# print("\nGOOG / GOOGL Correlation:")
# print(alphabet_correlation)

'''
GOOG and GOOGL represent two share classes of Alphabet.

Their 2025 daily-return correlation was approximately 0.998,
so including both would effectively give Alphabet two nearly
identical nodes in what is intended to be a company-level network.

So I'm dropping GOOG.
'''

full_daily_returns = full_daily_returns.drop(
    columns=["GOOG"]
)

# print("ANSS" in full_daily_returns.columns)
# print("GOOG" in full_daily_returns.columns)
# print("GOOGL" in full_daily_returns.columns)

# AMD / NVDA Rolling Correlation
amd_nvda_rolling_corr = (
    full_daily_returns["AMD"]
    .rolling(window=252)
    .corr(full_daily_returns["NVDA"])
)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    amd_nvda_rolling_corr.index,
    amd_nvda_rolling_corr
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1,
    alpha=0.7
)

ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("252-Day Rolling Correlation", fontsize=12)
ax.set_title(
    "AMD vs NVDA Rolling Return Correlation",
    fontsize=14,
    fontweight="bold"
)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/amd_nvda_rolling_correlation.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("\nFull Return Matrix Shape After Drop:")
print(full_daily_returns.shape)

full_correlation_matrix = full_daily_returns.corr(
    min_periods=200
)

print("\nFull Correlation Matrix Shape:")
print(full_correlation_matrix.shape)

# Removing redundant entries
print("\nNow we'll remove redundant entries.")

full_upper_triangle = np.triu(
    np.ones(full_correlation_matrix.shape),
    k=1
)

full_upper_triangle = full_upper_triangle.astype(bool)

full_upper_correlations = full_correlation_matrix.where(
    full_upper_triangle
)

full_correlation_pairs = full_upper_correlations.stack()

full_correlation_pairs.index.names = [
    "Stock_A",
    "Stock_B"
]

full_edge_table = full_correlation_pairs.reset_index()

full_edge_table.columns = [
    "Stock_A",
    "Stock_B",
    "Correlation"
]

full_edge_table = full_edge_table.sort_values(
    by="Correlation",
    ascending=False
)

full_edge_table = full_edge_table.reset_index(
    drop=True
)

print("\nNumber of unique pairs:")
print(len(full_correlation_pairs))

print("\nStrongest Relationships:")
print(full_edge_table.head(10))

print("\nWeakest Relationships:")
print(full_edge_table.tail(10))


# Trying to decide on a threshold
print("\nCorrelation Distribution:")
print(full_edge_table["Correlation"].describe())

print("\nCorrelation Quantiles:")

quantiles = full_edge_table["Correlation"].quantile(
    [0.50, 0.75, 0.90, 0.95, 0.99]
)

print(quantiles)


# Making a Histogram

# plt.style.use("seaborn-v0_8-whitegrid")

# fig, ax = plt.subplots(figsize=(10, 6))

# ax.hist(
#     full_edge_table["Correlation"],
#     bins=50,
#     color="#4C72B0",
#     edgecolor="white",
#     alpha=0.85
# )

# mean_corr = full_edge_table["Correlation"].mean()
# ax.axvline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Zero correlation")
# ax.axvline(mean_corr, color="crimson", linestyle="-", linewidth=1.5, label=f"Mean = {mean_corr:.3f}")

# ax.set_xlabel("Pairwise Return Correlation", fontsize=12)
# ax.set_ylabel("Number of Stock Pairs", fontsize=12)
# ax.set_title("Distribution of Pairwise Return Correlations", fontsize=14, fontweight="bold")
# ax.legend(frameon=False)

# for spine in ["top", "right"]:
#     ax.spines[spine].set_visible(False)

# plt.tight_layout()
# plt.savefig("figures/full_correlation_distribution.png", dpi=200, bbox_inches="tight")

# Making 4 Graphs
print("\nThe Four Graphs:")

def build_graph(edge_table, tickers, threshold):
    G = nx.Graph()

    G.add_nodes_from(tickers)

    for _, row in edge_table.iterrows():
        if row["Correlation"] >= threshold:
            G.add_edge(
                row["Stock_A"],
                row["Stock_B"],
                weight=row["Correlation"]
            )

    return G

regime_thresholds = {
    "Broad": full_edge_table["Correlation"].quantile(0.75),
    "Strong": full_edge_table["Correlation"].quantile(0.90),
    "Very Strong": full_edge_table["Correlation"].quantile(0.95),
    "Extreme": full_edge_table["Correlation"].quantile(0.99)
}

for regime, threshold in regime_thresholds.items():
    G = build_graph(
        full_edge_table,
        full_daily_returns.columns,
        threshold
    )

    active_nodes = [
        node
        for node, degree in G.degree()
        if degree > 0
    ]

    isolated_nodes = list(nx.isolates(G))

    components = list(nx.connected_components(G))

    nontrivial_components = [
        component
        for component in components
        if len(component) > 1
    ]

    nontrivial_components = sorted(
        nontrivial_components,
        key=len,
        reverse=True
    )

    print(f"\n{regime} Network")
    print(f"Threshold: {threshold:.4f}")
    print(f"Total Nodes: {G.number_of_nodes()}")
    print(f"Active Nodes: {len(active_nodes)}")
    print(f"Isolated Nodes: {len(isolated_nodes)}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Nontrivial Components: {len(nontrivial_components)}")

    if nontrivial_components:
        largest_component_size = len(
            nontrivial_components[0]
        )

        print(
            f"Largest Component: "
            f"{largest_component_size} nodes"
        )

        print("Largest Component Members:")
        print(
            sorted(nontrivial_components[0])
        )

        if regime == "Extreme":
            degree_ranking = sorted(
                [
                    (node, degree)
                    for node, degree in G.degree()
                    if degree > 0
                ],
                key=lambda item: item[1],
                reverse=True
            )

            print("\nExtreme Network Degree Ranking:")
            print(degree_ranking)

            print("\nExtreme Network Components:")
            print("___________________________")

            for component in nontrivial_components:
                print(
                    f"Size {len(component)}: "
                    f"{sorted(component)}"
                )

            print("\nExtreme Network Edges:")
            print("______________________")

            extreme_edge_table = full_edge_table[
                full_edge_table["Correlation"] >= threshold
            ].copy()

            extreme_edge_table = extreme_edge_table.sort_values(
                by="Correlation",
                ascending=False
            ).reset_index(drop=True)

            extreme_edge_table.insert(
                0,
                "Edge_ID",
                [
                    f"E{i:02d}"
                    for i in range(1, len(extreme_edge_table) + 1)
                ]
            )

            print(
                extreme_edge_table.to_string(
                    index=False
                )
            )

            print(
                f"\nTotal Extreme Edges: "
                f"{len(extreme_edge_table)}"
            )

            extreme_edge_table.to_csv(
                "outputs/extreme_edges_2016_2025.csv",
                index=False
            )

# Load the company industry tags
industry_df = pd.read_csv(
    "data/company_industries.csv"
)

# Create a dictionary mapping each ticker to its industry
industry_map = dict(
    zip(
        industry_df["Ticker"],
        industry_df["Industry"]
    )
)

# Add industry labels for both companies in every pair
full_edge_table["Industry_A"] = (
    full_edge_table["Stock_A"].map(industry_map)
)

full_edge_table["Industry_B"] = (
    full_edge_table["Stock_B"].map(industry_map)
)

# Mark whether each pair belongs to the same industry
full_edge_table["Same_Industry"] = (
    full_edge_table["Industry_A"]
    ==
    full_edge_table["Industry_B"]
)

print("\nSame vs Cross Industry Pair Counts:")
print(
    full_edge_table["Same_Industry"].value_counts()
)

print("\nCorrelation by Industry Relationship:")
print(
    full_edge_table
    .groupby("Same_Industry")["Correlation"]
    .describe()
)

# Keep only cross-industry pairs
cross_industry_edges = full_edge_table[
    full_edge_table["Same_Industry"] == False
].copy()

cross_industry_edges.to_csv(
    "outputs/cross_industry_edges_2016_2025.csv",
    index=False
)

print("\nCross-industry edges saved.")
print(f"Total cross-industry pairs: {len(cross_industry_edges)}")

mid_correlation_edges = cross_industry_edges[
    (cross_industry_edges["Correlation"] >= 0.4)
    &
    (cross_industry_edges["Correlation"] <= 0.5)
].copy()

print("\nCross-Industry Relationships Between 0.4 and 0.5:")
print(f"Number of pairs: {len(mid_correlation_edges)}")

mid_correlation_edges.to_csv(
    "outputs/mid_correlation_cross_industry_edges_2016_2025.csv",
    index=False
)

print("\nStrongest Cross-Industry Relationships:")
print(
    cross_industry_edges[
        [
            "Stock_A",
            "Stock_B",
            "Correlation",
            "Industry_A",
            "Industry_B"
        ]
    ]
    .head(30)
    .to_string(index=False)
)

# Create a standardized industry-pair label
full_edge_table["Industry_Pair"] = full_edge_table.apply(
    lambda row: " | ".join(
        sorted([
            row["Industry_A"],
            row["Industry_B"]
        ])
    ),
    axis=1
)

# Calculate baseline statistics for each industry pair
industry_pair_stats = (
    full_edge_table
    .groupby("Industry_Pair")["Correlation"]
    .agg(["count", "mean", "std"])
    .reset_index()
)

# Add the industry-pair statistics back to each edge
full_edge_table = full_edge_table.merge(
    industry_pair_stats,
    on="Industry_Pair",
    how="left"
)

# Calculate industry-adjusted anomaly score
full_edge_table["Industry_Z"] = (
    full_edge_table["Correlation"]
    -
    full_edge_table["mean"]
) / full_edge_table["std"]

# Keep cross-industry pairs with at least 5 comparison pairs
anomaly_candidates = full_edge_table[
    (full_edge_table["count"] >= 5)
    &
    (full_edge_table["Same_Industry"] == False)
    &
    (full_edge_table["std"].notna())
    &
    (full_edge_table["std"] > 0)
].copy()

# Focus on our 0.4 to 0.5 correlation range
mid_anomaly_candidates = anomaly_candidates[
    (anomaly_candidates["Correlation"] >= 0.4)
    &
    (anomaly_candidates["Correlation"] <= 0.5)
].copy()

# Rank by industry-adjusted anomaly score
mid_anomaly_candidates = mid_anomaly_candidates.sort_values(
    by="Industry_Z",
    ascending=False
)

mid_anomaly_candidates = mid_anomaly_candidates.reset_index(
    drop=True
)

print("\nTop Industry-Adjusted Anomalies Between 0.4 and 0.5:")
print(
    mid_anomaly_candidates[
        [
            "Stock_A",
            "Stock_B",
            "Correlation",
            "Industry_A",
            "Industry_B",
            "count",
            "mean",
            "std",
            "Industry_Z"
        ]
    ]
    .head(30)
    .to_string(index=False)
)

print("\nNumber of Mid-Correlation Anomaly Candidates:")
print(len(mid_anomaly_candidates))

mid_anomaly_candidates.to_csv(
    "outputs/mid_correlation_industry_anomalies_2016_2025.csv",
    index=False
)

print("\nIndustry Z Distribution:")
print(
    mid_anomaly_candidates["Industry_Z"].describe()
)

print("\nIndustry Z Quantiles:")
print(
    mid_anomaly_candidates["Industry_Z"].quantile(
        [0.50, 0.75, 0.90, 0.95, 0.99]
    )
)

anomaly_threshold = mid_anomaly_candidates[
    "Industry_Z"
].quantile(0.95)

forensic_candidates = mid_anomaly_candidates[
    mid_anomaly_candidates["Industry_Z"]
    >= anomaly_threshold
].copy()

print("\nForensic Candidates:")
print(f"Anomaly Threshold: {anomaly_threshold}")
print(f"Number of Candidates: {len(forensic_candidates)}")

print(
    forensic_candidates[
        [
            "Stock_A",
            "Stock_B",
            "Correlation",
            "Industry_A",
            "Industry_B",
            "Industry_Z"
        ]
    ].to_string(index=False)
)

forensic_candidates.to_csv(
    "outputs/forensic_candidates_2016_2025.csv",
    index=False
)


# ============================================================
# FINAL FIGURES
# ============================================================


# ============================================================
# FIGURE 1
# Distribution of Pairwise Correlations
# ============================================================

fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(
    full_edge_table["Correlation"].dropna(),
    bins=50,
    alpha=0.8,
    edgecolor="white"
)

# Add the four network thresholds
for regime, threshold in regime_thresholds.items():
    ax.axvline(
        threshold,
        linestyle="--",
        linewidth=1.5,
        label=f"{regime}: {threshold:.3f}"
    )

ax.set_xlabel(
    "Pairwise Daily-Return Correlation",
    fontsize=12
)

ax.set_ylabel(
    "Number of Stock Pairs",
    fontsize=12
)

ax.set_title(
    "Distribution of Pairwise Nasdaq-100 Return Correlations, 2016–2025",
    fontsize=14,
    fontweight="bold"
)

ax.legend(frameon=False)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/01_correlation_distribution.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 2
# Full Correlation Network
# ============================================================

full_network_threshold = regime_thresholds["Broad"]

G_full = build_graph(
    full_edge_table,
    full_daily_returns.columns,
    full_network_threshold
)

# Use a reproducible layout.
pos_full = nx.spring_layout(
    G_full,
    seed=42,
    weight="weight",
    iterations=300
)

# Get industries represented in the graph.
industries = sorted(
    set(
        industry_map.get(node, "Unknown")
        for node in G_full.nodes()
    )
)

# Assign each industry a numeric value for coloring.
industry_to_number = {
    industry: i
    for i, industry in enumerate(industries)
}

node_colors = [
    industry_to_number[
        industry_map.get(node, "Unknown")
    ]
    for node in G_full.nodes()
]

# Make more connected companies larger.
degrees = dict(G_full.degree())

node_sizes = [
    40 + degrees[node] * 12
    for node in G_full.nodes()
]

# Make stronger relationships thicker.
edge_weights = [
    G_full[u][v]["weight"]
    for u, v in G_full.edges()
]

if edge_weights:
    min_weight = min(edge_weights)
    max_weight = max(edge_weights)

    if max_weight > min_weight:
        edge_widths = [
            0.3 + 2.0 * (
                (weight - min_weight)
                /
                (max_weight - min_weight)
            )
            for weight in edge_weights
        ]
    else:
        edge_widths = [1.0 for weight in edge_weights]
else:
    edge_widths = []

fig, ax = plt.subplots(
    figsize=(18, 14)
)

nx.draw_networkx_edges(
    G_full,
    pos_full,
    width=edge_widths,
    alpha=0.20,
    ax=ax
)

nx.draw_networkx_nodes(
    G_full,
    pos_full,
    node_size=node_sizes,
    node_color=node_colors,
    cmap=plt.cm.tab20,
    alpha=0.85,
    ax=ax
)

nx.draw_networkx_labels(
    G_full,
    pos_full,
    font_size=7,
    ax=ax
)

ax.set_title(
    (
        "Nasdaq-100 Return Correlation Network, 2016–2025\n"
        f"Edges Represent Correlations Above the "
        f"75th Percentile "
        f"(ρ ≥ {full_network_threshold:.3f})"
    ),
    fontsize=16,
    fontweight="bold",
    pad=20
)

ax.axis("off")

plt.tight_layout()

plt.savefig(
    "figures/02_full_correlation_network.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 3
# Network Structure Across Four Correlation Thresholds
# ============================================================

regime_graphs = {}

for regime, threshold in regime_thresholds.items():
    regime_graphs[regime] = build_graph(
        full_edge_table,
        full_daily_returns.columns,
        threshold
    )

# Use one fixed layout for every network so that
# node positions stay consistent between panels.
broad_graph = regime_graphs["Broad"]

pos = nx.spring_layout(
    broad_graph,
    seed=42,
    weight="weight",
    iterations=200
)

fig, axes = plt.subplots(
    2,
    2,
    figsize=(16, 13)
)

axes = axes.flatten()

for ax, (regime, G) in zip(
    axes,
    regime_graphs.items()
):

    threshold = regime_thresholds[regime]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=30,
        alpha=0.7,
        ax=ax
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=0.8,
        alpha=0.35,
        ax=ax
    )

    ax.set_title(
        (
            f"{regime} Network\n"
            f"ρ ≥ {threshold:.3f} | "
            f"{G.number_of_edges()} edges"
        ),
        fontweight="bold"
    )

    ax.axis("off")

fig.suptitle(
    "Nasdaq-100 Correlation Network at Increasing Edge Thresholds",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "figures/03_network_thresholds.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 4
# Same-Industry vs Cross-Industry Correlations
# ============================================================

same_industry_corr = full_edge_table.loc[
    full_edge_table["Same_Industry"] == True,
    "Correlation"
].dropna()

cross_industry_corr = full_edge_table.loc[
    full_edge_table["Same_Industry"] == False,
    "Correlation"
].dropna()

fig, ax = plt.subplots(
    figsize=(8, 6)
)

ax.boxplot(
    [
        same_industry_corr,
        cross_industry_corr
    ],
    tick_labels=[
        "Same Industry",
        "Cross Industry"
    ],
    patch_artist=True,
    showfliers=False
)

ax.set_ylabel(
    "Pairwise Daily-Return Correlation",
    fontsize=12
)

ax.set_title(
    "Return Correlations Within and Across Industries",
    fontsize=14,
    fontweight="bold"
)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/04_same_vs_cross_industry.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 5
# Correlation vs Industry-Adjusted Anomaly Score
# ============================================================

fig, ax = plt.subplots(
    figsize=(11, 7)
)

# All eligible cross-industry relationships.
ax.scatter(
    anomaly_candidates["Correlation"],
    anomaly_candidates["Industry_Z"],
    alpha=0.35,
    s=30,
    label="Cross-industry pairs"
)

# Highlight final forensic candidates.
ax.scatter(
    forensic_candidates["Correlation"],
    forensic_candidates["Industry_Z"],
    s=80,
    alpha=0.9,
    label="Forensic candidates"
)

# Show the selected anomaly threshold.
ax.axhline(
    anomaly_threshold,
    linestyle="--",
    linewidth=1.5,
    label=f"95th percentile = {anomaly_threshold:.2f}"
)

# Label only the 10 strongest final candidates.
top_labels = forensic_candidates.nlargest(
    10,
    "Industry_Z"
)

for _, row in top_labels.iterrows():

    label = (
        f"{row['Stock_A']}-"
        f"{row['Stock_B']}"
    )

    ax.annotate(
        label,
        (
            row["Correlation"],
            row["Industry_Z"]
        ),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=8
    )

ax.set_xlabel(
    "Pairwise Return Correlation",
    fontsize=12
)

ax.set_ylabel(
    "Industry-Adjusted Z-Score",
    fontsize=12
)

ax.set_title(
    "Industry-Adjusted Cross-Industry Correlation Anomalies",
    fontsize=14,
    fontweight="bold"
)

ax.legend(frameon=False)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/05_industry_anomaly_scatter.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 6
# Ranked Forensic Candidates
# ============================================================

top_forensic = (
    forensic_candidates
    .nlargest(20, "Industry_Z")
    .copy()
)

top_forensic["Pair"] = (
    top_forensic["Stock_A"]
    +
    " — "
    +
    top_forensic["Stock_B"]
)

# Reverse order so the highest anomaly appears at the top.
top_forensic = top_forensic.sort_values(
    "Industry_Z",
    ascending=True
)

fig, ax = plt.subplots(
    figsize=(10, 8)
)

bars = ax.barh(
    top_forensic["Pair"],
    top_forensic["Industry_Z"]
)

for bar in bars:

    width = bar.get_width()

    ax.text(
        width + 0.02,
        bar.get_y() + bar.get_height() / 2,
        f"{width:.2f}",
        va="center",
        fontsize=8
    )

ax.set_xlabel(
    "Industry-Adjusted Z-Score",
    fontsize=12
)

ax.set_ylabel(
    "Stock Pair",
    fontsize=12
)

ax.set_title(
    "Top Cross-Industry Forensic Candidates",
    fontsize=14,
    fontweight="bold"
)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/06_forensic_candidate_ranking.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 7
# Rolling Correlation of Top Forensic Candidates
# ============================================================

top_rolling_pairs = (
    forensic_candidates
    .nlargest(5, "Industry_Z")
    [
        [
            "Stock_A",
            "Stock_B"
        ]
    ]
)

fig, ax = plt.subplots(
    figsize=(13, 7)
)

for _, row in top_rolling_pairs.iterrows():

    stock_a = row["Stock_A"]
    stock_b = row["Stock_B"]

    rolling_corr = (
        full_daily_returns[stock_a]
        .rolling(window=252)
        .corr(
            full_daily_returns[stock_b]
        )
    )

    ax.plot(
        rolling_corr.index,
        rolling_corr,
        linewidth=1.5,
        label=f"{stock_a} — {stock_b}"
    )

ax.axhline(
    0,
    linestyle="--",
    linewidth=1,
    alpha=0.6
)

ax.set_xlabel(
    "Date",
    fontsize=12
)

ax.set_ylabel(
    "252-Day Rolling Return Correlation",
    fontsize=12
)

ax.set_title(
    "Rolling Correlation of Top Forensic Candidates",
    fontsize=14,
    fontweight="bold"
)

ax.legend(
    frameon=False,
    loc="best"
)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()

plt.savefig(
    "figures/07_forensic_rolling_correlations.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()


print("\nFigures created:")
print("1. Correlation distribution")
print("2. Full correlation network")
print("3. Network threshold comparison")
print("4. Same-industry vs cross-industry correlations")
print("5. Industry-adjusted anomaly scatter")
print("6. Forensic candidate ranking")
print("7. Rolling correlations of top candidates")


print("\n~~~~~~~~~")
print("All Done!")
print("~~~~~~~~~")