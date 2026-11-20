'''
Howdy!

This is Part 3 of the Nasdaq-100 network investigation, and Part 3
is just this script.

Parts 1 and 2 used raw return correlations. Raw correlations include
the fact that the whole market tends to move together (the mean
pairwise correlation in 2025 was 0.28), so some of the edges I found
might be "just the market" rather than anything specific to the two
companies.

This script removes the market in two ways and rebuilds the same four
network regimes from Part 1 on what's left:

1. Market model: regress each stock on QQQ and keep the residuals.
2. PCA: remove the first 1, 2, and 3 principal components
   (PC1 is roughly the market; PC2 and PC3 are broad style moves).

Same population (99 companies), same year (2025), same regimes
(top 25% / 10% / 5% / 1%), so the only thing that changes is the
adjustment.

Parts 1 and 2 were written by hand before I started using Claude Code.
This script was written with Claude Code.

This was run with: /gpfs/home/guwechue/miniconda3/bin/python src/factor_adjusted.py > outputs/factor_adjusted_output.txt

Well Wishes,
DeDe
'''

import os

import yfinance as yf
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Market Network Investigation: Part 3!")
print("Removing the market and seeing what survives")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

os.makedirs("outputs", exist_ok=True)
os.makedirs("figures", exist_ok=True)

START = "2025-01-01"
END = "2026-01-01"
MARKET_TICKER = "QQQ"
PCA_COMPONENTS = [1, 2, 3]

REGIME_QUANTILES = {
    "Broad": 0.75,
    "Strong": 0.90,
    "Very Strong": 0.95,
    "Extreme": 0.99
}

# Pairs I talked about in Parts 1 and 2.
TRACKED_PAIRS = [
    ("KLAC", "LRCX"),
    ("ADP", "PAYX"),
    ("AVGO", "NVDA"),
    ("AMD", "NVDA"),
    ("GOOGL", "MSFT"),
    ("META", "MSFT"),
    ("CDNS", "SNPS"),
    ("AMZN", "GEHC"),
    ("CDW", "FTNT"),
    ("ADP", "XEL"),
]

AI_NAMES = ["NVDA", "AVGO", "AMD", "MSFT", "GOOGL", "META", "AMZN", "PLTR"]

# The persistent semiconductor core from Part 2.
SEMI_CORE = ["AMAT", "KLAC", "LRCX", "ADI", "MCHP", "NXPI", "ON", "TXN"]


# ------------------------------------------------------------------
# Data (same steps as full_100.py)
# ------------------------------------------------------------------

with open("data/nasdaq100_2025.txt", "r") as file:
    nasdaq_100_tickers = [
        line.strip()
        for line in file
        if line.strip()
    ]

full_data = yf.download(
    nasdaq_100_tickers + [MARKET_TICKER],
    start=START,
    end=END
)

all_close = full_data["Close"]

market_close = all_close[MARKET_TICKER]
full_close_prices = all_close[nasdaq_100_tickers]

missing_counts = full_close_prices.isna().sum()

usable_tickers = [
    ticker
    for ticker in nasdaq_100_tickers
    if missing_counts[ticker] < len(full_close_prices)
]

print("\nUnusable tickers (all values missing):")
print(sorted(set(nasdaq_100_tickers) - set(usable_tickers)))

full_daily_returns = (
    full_close_prices[usable_tickers]
    .pct_change()
    .dropna()
)

# Same decision as Part 1: one node per company.
full_daily_returns = full_daily_returns.drop(columns=["GOOG"])

market_returns = (
    market_close
    .pct_change()
    .reindex(full_daily_returns.index)
)

if market_returns.isna().any():
    raise ValueError("QQQ returns are missing on some trading days.")

n_days, n_companies = full_daily_returns.shape

print("\nReturn Matrix Shape:")
print(full_daily_returns.shape)

print(
    "\nNote: Part 1 had 99 companies. Yahoo no longer serves history "
    "for tickers delisted since then\n(EA went private Aug 2026; WBD "
    "was acquired by Skydance Oct 2026), so the Raw version below\n"
    "is recomputed on the companies available today to keep the "
    "comparison apples to apples."
)


# ------------------------------------------------------------------
# Removing the market
# ------------------------------------------------------------------

def market_model_residuals(returns, market):
    '''
    For each stock: r_i = a_i + b_i * r_QQQ + e_i.
    Returns the residuals e_i and the betas b_i.
    '''
    X = np.column_stack([
        np.ones(len(market)),
        market.values
    ])

    coefficients, _, _, _ = np.linalg.lstsq(
        X,
        returns.values,
        rcond=None
    )

    residuals = returns.values - X @ coefficients

    betas = pd.Series(
        coefficients[1],
        index=returns.columns,
        name="Beta"
    )

    residuals = pd.DataFrame(
        residuals,
        index=returns.index,
        columns=returns.columns
    )

    return residuals, betas


def standardized_svd(returns):
    '''
    PCA on standardized returns (equivalent to PCA of the
    correlation matrix).
    '''
    Z = (returns - returns.mean()) / returns.std()

    U, S, Vt = np.linalg.svd(
        Z.values,
        full_matrices=False
    )

    return Z, U, S, Vt


def pca_residuals(Z, U, S, Vt, k):
    '''
    Removes the first k principal components from the
    standardized returns.
    '''
    top_k = (U[:, :k] * S[:k]) @ Vt[:k]

    residuals = Z.values - top_k

    return pd.DataFrame(
        residuals,
        index=Z.index,
        columns=Z.columns
    )


market_residuals, market_betas = market_model_residuals(
    full_daily_returns,
    market_returns
)

Z, U, S, Vt = standardized_svd(full_daily_returns)

explained_variance = S ** 2 / np.sum(S ** 2)

print("\nVariance Explained by the First 5 Principal Components:")

for i in range(5):
    print(
        f"PC{i + 1}: {explained_variance[i]:.3f} "
        f"(cumulative {explained_variance[:i + 1].sum():.3f})"
    )

# PC1 should look like the market. Quick check:
pc1_scores = pd.Series(U[:, 0] * S[0], index=Z.index)
pc1_market_corr = abs(pc1_scores.corr(market_returns))

print(f"\n|Correlation| between PC1 and QQQ returns: {pc1_market_corr:.3f}")

print("\nMarket Betas (vs QQQ):")
print(market_betas.describe())

print("\nHighest Betas:")
print(market_betas.sort_values(ascending=False).head(10).round(3))

# Each version: (returns to correlate, number of factors removed).
versions = {
    "Raw": (full_daily_returns, 0),
    "Market (QQQ)": (market_residuals, 1),
}

for k in PCA_COMPONENTS:
    versions[f"PCA-{k}"] = (
        pca_residuals(Z, U, S, Vt, k),
        k
    )


# ------------------------------------------------------------------
# Network helpers (same logic as full_100.py)
# ------------------------------------------------------------------

def edge_table_from_returns(returns):
    correlation_matrix = returns.corr()

    upper_triangle = np.triu(
        np.ones(correlation_matrix.shape),
        k=1
    ).astype(bool)

    pairs = correlation_matrix.where(upper_triangle).stack().dropna()
    pairs.index.names = ["Stock_A", "Stock_B"]

    edge_table = pairs.reset_index()
    edge_table.columns = ["Stock_A", "Stock_B", "Correlation"]

    edge_table = edge_table.sort_values(
        by="Correlation",
        ascending=False
    ).reset_index(drop=True)

    return edge_table


def build_graph(edge_table, tickers, threshold):
    G = nx.Graph()
    G.add_nodes_from(tickers)

    strong = edge_table[edge_table["Correlation"] >= threshold]

    for a, b, r in zip(
        strong["Stock_A"],
        strong["Stock_B"],
        strong["Correlation"]
    ):
        G.add_edge(a, b, weight=r)

    return G


def nontrivial_components(G):
    components = [
        c for c in nx.connected_components(G)
        if len(c) > 1
    ]

    return sorted(components, key=len, reverse=True)


def pair_key(a, b):
    return "-".join(sorted([a, b]))


def fisher_interval(r, n_eff):
    '''
    Approximate 95% confidence interval for a correlation
    using the Fisher z-transform.
    '''
    z = np.arctanh(r)
    se = 1 / np.sqrt(n_eff - 3)

    return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)


# ------------------------------------------------------------------
# Running every version
# ------------------------------------------------------------------

tickers = list(full_daily_returns.columns)

summary_rows = []
extreme_edge_tables = []
extreme_graphs = {}
edge_tables = {}

for version, (returns, k_removed) in versions.items():

    edge_table = edge_table_from_returns(returns)
    edge_tables[version] = edge_table

    correlations = edge_table["Correlation"]

    print("\n==================================================")
    print(f"{version}")
    print("==================================================")

    print("\nCorrelation Distribution:")
    print(correlations.describe().round(4))

    summary = {
        "Version": version,
        "Factors_Removed": k_removed,
        "Mean": correlations.mean(),
        "Median": correlations.median(),
        "Std": correlations.std(),
        "Share_Negative": (correlations < 0).mean(),
    }

    for regime, q in REGIME_QUANTILES.items():

        threshold = correlations.quantile(q)

        G = build_graph(edge_table, tickers, threshold)

        components = nontrivial_components(G)

        active_nodes = [
            node for node, degree in G.degree()
            if degree > 0
        ]

        largest_size = len(components[0]) if components else 0

        print(f"\n{regime} Network")
        print(f"Threshold: {threshold:.4f}")
        print(f"Active Nodes: {len(active_nodes)}")
        print(f"Isolated Nodes: {n_companies - len(active_nodes)}")
        print(f"Edges: {G.number_of_edges()}")
        print(f"Nontrivial Components: {len(components)}")
        print(f"Largest Component: {largest_size} nodes")

        summary[f"{regime}_Threshold"] = threshold
        summary[f"{regime}_Edges"] = G.number_of_edges()
        summary[f"{regime}_Active"] = len(active_nodes)
        summary[f"{regime}_Components"] = len(components)
        summary[f"{regime}_Largest"] = largest_size

        if regime != "Extreme":
            continue

        extreme_graphs[version] = G

        print("\nExtreme Network Components:")
        print("___________________________")

        for component in components:
            print(f"Size {len(component)}: {sorted(component)}")

        extreme = edge_table[
            edge_table["Correlation"] >= threshold
        ].copy()

        n_eff = n_days - k_removed

        intervals = extreme["Correlation"].apply(
            lambda r: fisher_interval(r, n_eff)
        )

        extreme["CI_Low"] = [low for low, _ in intervals]
        extreme["CI_High"] = [high for _, high in intervals]

        # If the lower end of the interval falls below the
        # threshold, the edge could plausibly be on the other side.
        extreme["Near_Threshold"] = extreme["CI_Low"] < threshold

        extreme.insert(0, "Version", version)

        print("\nExtreme Network Edges (with 95% intervals):")
        print("_____________________________________________")
        print(
            extreme[
                [
                    "Stock_A",
                    "Stock_B",
                    "Correlation",
                    "CI_Low",
                    "CI_High",
                    "Near_Threshold"
                ]
            ]
            .round(3)
            .to_string(index=False)
        )

        summary["Extreme_Near_Threshold"] = int(
            extreme["Near_Threshold"].sum()
        )

        extreme_edge_tables.append(extreme)

    summary_rows.append(summary)

summary_df = pd.DataFrame(summary_rows)
extreme_df = pd.concat(extreme_edge_tables, ignore_index=True)


# ------------------------------------------------------------------
# Which Part 1 Extreme edges survive?
# ------------------------------------------------------------------

print("\n==================================================")
print("Do the Part 1 Extreme Edges Survive?")
print("==================================================")

extreme_sets = {
    version: set(
        pair_key(a, b)
        for a, b in zip(group["Stock_A"], group["Stock_B"])
    )
    for version, group in extreme_df.groupby("Version", sort=False)
}

raw_extreme = extreme_sets["Raw"]

survival_rows = []

for version, edges in extreme_sets.items():

    if version == "Raw":
        continue

    survived = raw_extreme & edges
    lost = raw_extreme - edges
    new = edges - raw_extreme

    print(f"\n{version}")
    print(
        f"Raw Extreme edges still in this version's top 1%: "
        f"{len(survived)} of {len(raw_extreme)} "
        f"({len(survived) / len(raw_extreme):.0%})"
    )
    print(f"Lost: {sorted(lost)}")
    print(f"New Extreme edges (not in Raw top 1%): {sorted(new)}")

    survival_rows.append({
        "Version": version,
        "Raw_Extreme_Edges": len(raw_extreme),
        "Survived": len(survived),
        "Survival_Rate": len(survived) / len(raw_extreme),
        "Lost": len(lost),
        "New": len(new),
        "Lost_Edges": "; ".join(sorted(lost)),
        "New_Edges": "; ".join(sorted(new)),
    })

survival_df = pd.DataFrame(survival_rows)

summary_df = summary_df.merge(
    survival_df[["Version", "Survived", "Survival_Rate", "New"]],
    on="Version",
    how="left"
)


# ------------------------------------------------------------------
# Semiconductor core and AI names
# ------------------------------------------------------------------

print("\n==================================================")
print("Semiconductor Core and AI Names (Extreme Networks)")
print("==================================================")

semi_core = [t for t in SEMI_CORE if t in tickers]
ai_names = [t for t in AI_NAMES if t in tickers]

ai_rows = []

for version, G in extreme_graphs.items():

    components = nontrivial_components(G)

    # Component holding the most semiconductor-core companies.
    best_component = max(
        components,
        key=lambda c: len(c & set(semi_core)),
        default=set()
    )

    core_together = len(best_component & set(semi_core))

    print(f"\n{version}")
    print(
        f"Semiconductor core companies in one component: "
        f"{core_together} of {len(semi_core)}"
    )
    print(f"That component ({len(best_component)} nodes): {sorted(best_component)}")

    summary_df.loc[
        summary_df["Version"] == version,
        "Semi_Core_Together"
    ] = core_together

    for ticker in ai_names:

        component = next(
            (c for c in components if ticker in c),
            set()
        )

        neighbors = sorted(G.neighbors(ticker))

        ai_rows.append({
            "Version": version,
            "Ticker": ticker,
            "Degree": G.degree(ticker),
            "Component_Size": len(component),
            "Neighbors": ", ".join(neighbors),
        })

        print(
            f"  {ticker}: degree {G.degree(ticker)}, "
            f"neighbors {neighbors}"
        )

ai_df = pd.DataFrame(ai_rows)


# ------------------------------------------------------------------
# Tracked pairs from Parts 1 and 2
# ------------------------------------------------------------------

print("\n==================================================")
print("Tracked Pairs From Parts 1 and 2")
print("==================================================")
print(
    f"Percentile = share of all {n_companies * (n_companies - 1) // 2:,} "
    "pairs with a lower correlation in that version.\nPercentiles are easier to compare across "
    "versions because the whole distribution shifts."
)

tracked_rows = []

for version, edge_table in edge_tables.items():

    lookup = {
        pair_key(a, b): r
        for a, b, r in zip(
            edge_table["Stock_A"],
            edge_table["Stock_B"],
            edge_table["Correlation"]
        )
    }

    all_correlations = edge_table["Correlation"].values

    for a, b in TRACKED_PAIRS:

        key = pair_key(a, b)

        if key not in lookup:
            continue

        r = lookup[key]

        tracked_rows.append({
            "Version": version,
            "Pair": f"{a}-{b}",
            "Correlation": r,
            "Percentile": (all_correlations < r).mean(),
        })

tracked_df = pd.DataFrame(tracked_rows)

print("\nCorrelation:")
print(
    tracked_df
    .pivot(index="Pair", columns="Version", values="Correlation")
    [list(versions)]
    .round(3)
    .to_string()
)

print("\nPercentile:")
print(
    tracked_df
    .pivot(index="Pair", columns="Version", values="Percentile")
    [list(versions)]
    .round(3)
    .to_string()
)


# ------------------------------------------------------------------
# Do the Part 2 industry anomalies survive?
# ------------------------------------------------------------------

print("\n==================================================")
print("Do the Part 2 Industry Anomalies Survive?")
print("==================================================")

anomaly_df = pd.DataFrame()

if os.path.exists("data/company_industries.csv"):

    industry_df = pd.read_csv("data/company_industries.csv")

    industry_map = dict(
        zip(industry_df["Ticker"], industry_df["Industry"])
    )

    part2_candidates = None

    if os.path.exists("outputs/forensic_candidates.csv"):
        part2 = pd.read_csv("outputs/forensic_candidates.csv")
        part2_candidates = set(
            pair_key(a, b)
            for a, b in zip(part2["Stock_A"], part2["Stock_B"])
        )
        print(f"\nLoaded {len(part2_candidates)} Part 2 forensic candidates.")
    else:
        print(
            "\noutputs/forensic_candidates.csv not found; "
            "only tracking the named pairs."
        )

    anomaly_rows = []

    for version, edge_table in edge_tables.items():

        table = edge_table.copy()

        table["Industry_A"] = table["Stock_A"].map(industry_map)
        table["Industry_B"] = table["Stock_B"].map(industry_map)

        table = table.dropna(subset=["Industry_A", "Industry_B"])

        table["Same_Industry"] = table["Industry_A"] == table["Industry_B"]

        table["Industry_Pair"] = [
            " | ".join(sorted([a, b]))
            for a, b in zip(table["Industry_A"], table["Industry_B"])
        ]

        stats = (
            table
            .groupby("Industry_Pair")["Correlation"]
            .agg(["count", "mean", "std"])
            .reset_index()
        )

        table = table.merge(stats, on="Industry_Pair", how="left")

        table["Industry_Z"] = (
            (table["Correlation"] - table["mean"]) / table["std"]
        )

        # Same filters as Part 2, but over all cross-industry pairs
        # (the 0.4-0.5 window from Part 2 was in raw correlation
        # units, which don't carry over once the market is removed).
        cross = table[
            (table["count"] >= 5)
            & (~table["Same_Industry"])
            & (table["std"] > 0)
        ].copy()

        cutoff = cross["Industry_Z"].quantile(0.95)

        cross["Top_5pct"] = cross["Industry_Z"] >= cutoff
        cross["Z_Percentile"] = cross["Industry_Z"].rank(pct=True)

        cross["Key"] = [
            pair_key(a, b)
            for a, b in zip(cross["Stock_A"], cross["Stock_B"])
        ]

        if part2_candidates:
            in_part2 = cross[cross["Key"].isin(part2_candidates)]
            still_top = int(in_part2["Top_5pct"].sum())

            print(
                f"\n{version}: {still_top} of {len(in_part2)} Part 2 "
                f"candidates are in the top 5% of industry-adjusted "
                f"scores"
            )

            summary_df.loc[
                summary_df["Version"] == version,
                "Part2_Anomalies_Top5pct"
            ] = still_top

        named = [pair_key("AMZN", "GEHC"), pair_key("CDW", "FTNT")]

        for _, row in cross[cross["Key"].isin(named)].iterrows():

            print(
                f"  {row['Stock_A']}-{row['Stock_B']}: "
                f"r = {row['Correlation']:.3f}, "
                f"industry z = {row['Industry_Z']:.2f}, "
                f"percentile = {row['Z_Percentile']:.3f}"
            )

        keep = cross["Key"].isin(named)

        if part2_candidates:
            keep = keep | cross["Key"].isin(part2_candidates)

        subset = cross.loc[
            keep,
            [
                "Stock_A",
                "Stock_B",
                "Correlation",
                "Industry_Z",
                "Z_Percentile",
                "Top_5pct"
            ]
        ].copy()

        subset.insert(0, "Version", version)
        anomaly_rows.append(subset)

    anomaly_df = pd.concat(anomaly_rows, ignore_index=True)

else:
    print("\ndata/company_industries.csv not found; skipping.")


# ------------------------------------------------------------------
# Figures
# ------------------------------------------------------------------

plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(10, 6))

for version, color in [
    ("Raw", "#4C72B0"),
    ("Market (QQQ)", "#DD8452"),
    ("PCA-3", "#55A868"),
]:
    correlations = edge_tables[version]["Correlation"]

    ax.hist(
        correlations,
        bins=60,
        histtype="step",
        linewidth=2,
        color=color,
        label=f"{version} (mean = {correlations.mean():.3f})"
    )

ax.axvline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.set_xlabel("Pairwise Return Correlation", fontsize=12)
ax.set_ylabel("Number of Stock Pairs", fontsize=12)
ax.set_title(
    "Pairwise Correlations Before and After Removing the Market",
    fontsize=14,
    fontweight="bold"
)
ax.legend(frameon=False)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig(
    "figures/factor_adjusted_distribution.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close()


def draw_extreme_network(G, title, path):
    active = [node for node, degree in G.degree() if degree > 0]
    H = G.subgraph(active)

    components = nontrivial_components(H)
    palette = plt.cm.tab10.colors

    colors = {}
    for i, component in enumerate(components):
        for node in component:
            colors[node] = palette[i % len(palette)]

    fig, ax = plt.subplots(figsize=(12, 10))

    # Lay out each component on its own tile of a grid so that
    # edges from one component never pass through another.
    n_tiles = len(components)
    n_cols = int(np.ceil(np.sqrt(n_tiles)))

    pos = {}

    for i, component in enumerate(components):
        sub = H.subgraph(component)

        sub_pos = nx.spring_layout(sub, seed=42)

        coords = np.array(list(sub_pos.values()))
        coords = coords - coords.mean(axis=0)

        scale = np.abs(coords).max()
        if scale > 0:
            coords = coords / scale

        # Bigger components get a bit more room inside their tile.
        coords = coords * (0.25 + 0.15 * min(len(component), 15) / 15)

        row, col = divmod(i, n_cols)
        center = np.array([col, -row])

        for node, xy in zip(sub_pos, coords):
            pos[node] = center + xy

    nx.draw_networkx_edges(H, pos, alpha=0.4, ax=ax)
    nx.draw_networkx_nodes(
        H,
        pos,
        node_color=[colors[n] for n in H.nodes],
        node_size=500,
        ax=ax
    )
    nx.draw_networkx_labels(H, pos, font_size=8, ax=ax)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()


draw_extreme_network(
    extreme_graphs["Raw"],
    "Raw Extreme Network (top 1%)",
    "figures/extreme_network_raw.png"
)

draw_extreme_network(
    extreme_graphs["Market (QQQ)"],
    "Market-Adjusted Extreme Network (top 1%)",
    "figures/extreme_network_market_adjusted.png"
)


# ------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------

summary_df.to_csv("outputs/factor_adjusted_summary.csv", index=False)
extreme_df.to_csv("outputs/factor_adjusted_extreme_edges.csv", index=False)
survival_df.to_csv("outputs/factor_adjusted_edge_survival.csv", index=False)
tracked_df.to_csv("outputs/factor_adjusted_tracked_pairs.csv", index=False)
ai_df.to_csv("outputs/factor_adjusted_ai_names.csv", index=False)
market_betas.to_csv("outputs/market_betas.csv")

pd.DataFrame({
    "Component": [f"PC{i + 1}" for i in range(10)],
    "Explained_Variance": explained_variance[:10],
    "Cumulative": np.cumsum(explained_variance[:10]),
}).to_csv("outputs/pca_explained_variance.csv", index=False)

if not anomaly_df.empty:
    anomaly_df.to_csv(
        "outputs/factor_adjusted_anomalies.csv",
        index=False
    )


# ------------------------------------------------------------------
# Headline numbers
# ------------------------------------------------------------------

print("\n==================================================")
print("Headline Numbers")
print("==================================================")

columns = [
    "Version",
    "Mean",
    "Share_Negative",
    "Extreme_Threshold",
    "Extreme_Largest",
    "Extreme_Near_Threshold",
    "Survived",
    "Survival_Rate",
    "Semi_Core_Together",
]

if "Part2_Anomalies_Top5pct" in summary_df.columns:
    columns.append("Part2_Anomalies_Top5pct")

print(summary_df[columns].round(3).to_string(index=False))

print(f"\nPC1 explains {explained_variance[0]:.1%} of daily return variance.")

print("\n~~~~~~~~~")
print("All Done!")
print("~~~~~~~~~")