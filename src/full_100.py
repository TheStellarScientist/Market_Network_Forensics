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

This was run with: /gpfs/home/guwechue/miniconda3/bin/python src/full_100.py > outputs/full_100_output.txt

Well Wishes,
My Name
'''

import yfinance as yf
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Market Network Investigation!")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

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
    start="2025-01-01",
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
    .pct_change()
    .dropna()
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

print("\nFull Return Matrix Shape After Drop:")
print(full_daily_returns.shape)

full_correlation_matrix = full_daily_returns.corr()

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
            
print("\n~~~~~~~~~")
print("All Done!")
print("~~~~~~~~~")