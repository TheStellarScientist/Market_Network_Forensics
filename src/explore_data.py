'''
Howdy! 

The purpose of this script is to investigate the data I'm
importing from yfinance. We'll be using the Nasdaq-100 as
the starting population. 

This script is part 1 and focused on a sample of 10 for
exploration purposes. 

Question: 
Does an AI-related ecosystem emerge from the return network
without us explicitly telling the algorithm what an
"AI Company" is?

We're essentially doing some Forensic Network Science. 

This was run with: /gpfs/home/guwechue/miniconda3/bin/python src/explore_data.py > outputs/explore_data_output.txt

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


'''
We're starting with one stuck to make sure yfinance works properly. 
After that we'll look at a small sample, and then eventually the whole
population.
'''

# Single Stock - Nvidia

ticker = "NVDA"

data = yf.download(
    ticker,
    start='2025-01-01',
    end='2026-01-01'
)

print("Nvidia Inspection")
print("__________________")

print("This is the data available for Nvdia from Jan 1st 2025 to Dec 31st 2025:")

print(data)

# Uncomment as needed for the following.

# The beginning of the data:
# print(data.head())

# The end of the data:
# print(data.tail())

# The shape of the data (it's a tuple):
# print(data.shape)

# Sample Investigation: 10 Stocks

print("Sample Investigation")
print("______________________")

print('''
We'll now investigate a sample of 10 companies:

Companies in the center of AI:
1. NVDA - Nvidia (GPUs/compute)
2. MSFT - Microsoft (OpenAI stake, Azure AI)
3. GOOGL - Alphabet (DeepMind, Gemini, TPUs)
4. AVGO - Broadcom (AI networking/custom silicon)
5. AMD - Advanced Micro Devices (AI Chips, Nvidia's rival)

Companies on the edge of AI:
6. ORCL - Oracle (Stargate partnership, GPU deals)
7. META - Meta (Heavy on AI but it's just social media)
8. PLTR - Palantir (AI/data analytics)

Companies removed from AI:
9. PEP - PepsiCo (Drinks, should be an outlier)
10. COST - Costco (Retail, second outlier)

''')

tickers = ["NVDA", "MSFT", "GOOGL", "AVGO", "AMD", "ORCL", "META", "PLTR", "PEP", "COST"]

sample_data = yf.download(
    tickers,
    start='2025-01-01',
    end='2026-01-01'
)

print("\nFirst five rows:")
print(sample_data.head())

print("\nShape:")
print(sample_data.shape)

print("\nColumns:")
print(sample_data.columns)

print('''
To compare the companies and draw relationships, we want returns, not
raw prices. Two companies can have their stock go down by $20 but if one
was originally $120 and the other $420, they are not comparable. 

We'll work around this with returns because they show percentages.
''')

# Extracting Close
close_prices = sample_data["Close"]

print("\nClosing Prices:")
print(close_prices.head())

print("\nClosing Price Shape:")
print(close_prices.shape)

print("\nClosing Price Columns:")
print(close_prices.columns)

# Calculating returns manually for a quick sanity check

amd_return = (close_prices.iloc[1, 0] / close_prices.iloc[0, 0]) - 1
# Should be - amd_return = (125.370003 / 120.629997) - 1

print("\nManually calculated AMD return:")
print(amd_return)

# Doing it properly now with Pandas
daily_returns = close_prices.pct_change()

print("\nDaily Returns:")
print(daily_returns.head())

# Closed market on Jan 1st so we can't calculate returns.
daily_returns = daily_returns.dropna()

print("\nClean Daily Returns:")
print(daily_returns.head())

print("\nReturn Shape:")
print(daily_returns.shape)

# We'll use correlation to draw the network.
correlation_matrix = daily_returns.corr()

print("\nCorrelation Matrix:")
print(correlation_matrix)

print("\nCorrelation Matrix Shape:")
print(correlation_matrix.shape)

# Removing redundant entries
print("Now we'll remove redundant entries.")

upper_triangle = np.triu(
    np.ones(correlation_matrix.shape),
    k=1
)

print("\nUpper Triangle Mask:")
print(upper_triangle)

upper_triangle = upper_triangle.astype(bool)
upper_correlations = correlation_matrix.where(upper_triangle)

print("\nUpper Correlations:")
print(upper_correlations)

correlation_pairs = upper_correlations.stack()

print("\nCorrelation Pairs:")
print(correlation_pairs)

print("\nNumber of unique pairs:")
print(len(correlation_pairs))


# Turning them from pandas series with a MultiIndex to regular columns

correlation_pairs.index.names = ["Stock_A", "Stock_B"]

edge_table = correlation_pairs.reset_index()
edge_table.columns = ["Stock_A", "Stock_B", "Correlation"]

print("\nEdge Table:")
print(edge_table.head())

edge_table = edge_table.sort_values(
    by="Correlation",
    ascending=False
)

edge_table = edge_table.reset_index(drop=True)

print("\nStrongest Relationships:")
print(edge_table.head(10))

print("\nWeakest Relationships:")
print(edge_table.tail(10))

# Building the graph

print("\nGraph Attributes Below:")

G = nx.Graph()
G.add_nodes_from(tickers)

print(G.nodes)

# This threshold is currently arbitary. It's a work in progress.
# threshold = 0.5

# for _, row in edge_table.iterrows():
#     if row["Correlation"] >= threshold:
#         G.add_edge(
#             row["Stock_A"],
#             row["Stock_B"],
#             weight=row["Correlation"]
#         )

# print("\nNodes:")
# print(G.nodes)

# print("\nEdges:")
# print(G.edges(data=True))

# print("\nNumber of nodes:")
# print(G.number_of_nodes())

# print("\nNumber of edges:")
# print(G.number_of_edges())

# print("\nDegrees:")
# print(dict(G.degree()))

# degree_ranking = sorted(
#     G.degree(),
#     key=lambda item: item[1],
#     reverse=True
# )

# print("\nDegree Ranking:")
# print(degree_ranking)

# components = list(nx.connected_components(G))

# print("\nConnected Components:")
# print(components)

# print("\nNumber of Components:")
# print(len(components))

# Looking for a real threshold now.

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

# Sanity check after refactoring the code.

# G = build_graph(
#     edge_table,
#     tickers,
#     0.5
# )

# print("\nFunction Test:")
# print("Nodes:", G.number_of_nodes())
# print("Edges:", G.number_of_edges())

# Threshold sensitivity

#thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

# print("\nThreshold Sensitivity")
# print("______________________________________________")
# print("Threshold | Edges | NVDA Degree | GOOGL Degree")

# for threshold in thresholds:
#     G = build_graph(
#         edge_table,
#         tickers,
#         threshold
#     )

#     nvda_degree = G.degree("NVDA")
#     googl_degree = G.degree("GOOGL")

#     print(
#         f"{threshold} | "
#         f"{G.number_of_edges()} | "
#         f"{nvda_degree} | "
#         f"{googl_degree}"
#     )

# Looking at all the results and turning them into dictionaries

thresholds = np.arange(0.30, 0.71, 0.01)
threshold_results = []

for threshold in thresholds:
    G = build_graph(
        edge_table,
        tickers,
        threshold
    )

    result = {
    "Threshold": round(threshold, 2),
    "Edges": G.number_of_edges()
    }

    for ticker in tickers:
        result[ticker] = G.degree(ticker)

    threshold_results.append(result)

threshold_df = pd.DataFrame(threshold_results)

print("\nThreshold Sensitivity - All Nodes")
print("_____________________________________")
print(threshold_df)

transition_thresholds = sorted(
    edge_table.loc[
        edge_table["Correlation"] > 0,
        "Correlation"
    ].unique()
)

print("\nExact Transition Thresholds:")

for threshold in transition_thresholds:
    print(f"{threshold:.4f}")










# Drawing the graph
# threshold_df.plot(
#     x="Threshold",
#     y=tickers,
#     figsize=(12, 8),
#     marker="."
# )

# plt.ylabel("Degree")
# plt.title("Node Degree Across Correlation Thresholds")
# plt.grid(True)
# plt.tight_layout()

# plt.savefig(
#     "figures/threshold_sensitivity.png",
#     bbox_inches="tight"
# )

# # Extracting fata for Google to test the figure:
# googl_edges = edge_table[
#     (edge_table["Stock_A"] == "GOOGL") |
#     (edge_table["Stock_B"] == "GOOGL")
# ]

# print("\nGOOGL Relationships:")
# print(googl_edges)



# plt.figure(figsize=(10, 8))

# pos = nx.spring_layout(G, seed=42)

# nx.draw(
#     G,
#     pos,
#     with_labels=True
# )

# plt.savefig(
#     "figures/sample_network.png",
#     bbox_inches="tight"
# )


# Edge Weights
# weighted_degree = dict(G.degree(weight="weight"))

# print("\nWeighted Degrees:")
# print(weighted_degree)

# strength_ranking = sorted(
#     weighted_degree.items(),
#     key=lambda item: item[1],
#     reverse=True
# )

# print("\nStrength Ranking:")
# print(strength_ranking)



print("\n~~~~~~~~~")
print("All Done!")
print("~~~~~~~~~")