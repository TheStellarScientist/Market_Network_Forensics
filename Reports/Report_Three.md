# Hidden Structure in the Nasdaq-100 #3

> Part 2 ended with "this project is done!" It was, mostly. But one question started bugging me when I reviewed this project months later, and I wanted a quick answer to it before moving on.

> Parts 1 and 2 were written by hand before I started using Claude Code. Part 3 is just one script, `src/factor_adjusted.py`, and it was written with Claude Code.

## The Question

Every network in Parts 1 and 2 was built from raw return correlations.

The problem is that on most days the whole market moves together. In 2025 the average correlation between two random Nasdaq-100 companies was about 0.28. Some of that is just "stocks went up today" rather than anything specific to those two companies.

So the question for Part 3 is:

*How much of the structure from Parts 1 and 2 was just the market?*

---

# Method

I removed the shared market movement from every stock's returns, then rebuilt the exact same networks from what's left.

1. **Market model (main version).** For each stock, regress its daily returns on QQQ (the Nasdaq-100 ETF) and keep the residuals:

$$
r_i = \alpha_i + \beta_i \, r_{\mathrm{QQQ}} + \varepsilon_i
$$

The network is then built from correlations between the $\varepsilon_i$.

2. **PCA (robustness check).** Remove the first 1, 2, or 3 principal components of the standardized returns. PC1 is basically the market: it explains 32.1% of daily return variance, and its correlation with QQQ is 0.94. PC2 (9.9%) and PC3 (4.2%) are broader "style" movements.

Everything else stays the same as Part 1: the same year (2025), the same four regimes (top 25% / 10% / 5% / 1% of pairs), and the same connected-component analysis. The only thing that changes is the adjustment.

## Population Change: 97 Companies Instead of 99

Two companies from the 2025 population have been delisted since Parts 1 and 2, and `yfinance` no longer serves their history:

* **EA**: taken private by a PIF / Silver Lake / Affinity Partners consortium in August 2026
* **WBD**: acquired by Skydance in October 2026

To keep the comparison fair, the Raw version in this part is recomputed on the same 97 companies. That's why the raw numbers below differ slightly from Part 1 (mean 0.2848 instead of 0.2817; 47 Extreme edges instead of 49). The structure is otherwise the same: the same 15-node semiconductor component and the same six smaller components.

## Two Things to Keep in Mind When Reading PCA Results

* PCA versions always have an average correlation of about 0. Removing components forces that mathematically, so it isn't anything interesting.
* Removing PC2 or PC3 can strip out industry structure. With a large semiconductor group in the population, a component can easily become "semiconductors vs. everything else." So if something disappears under PCA-3, that doesn't mean it was fake.

That's why the market model is the main version, and PCA is there to check how robust the results are.

---

# Result 1: Most of the Average Correlation Was the Market

| Version | Mean correlation | Share of pairs < 0 | Extreme threshold | Largest Extreme component |
|---|---:|---:|---:|---:|
| Raw | 0.285 | 6.7% | 0.676 | 15 |
| Market (QQQ) | 0.054 | 38.9% | 0.490 | 7 |
| PCA-1 | −0.006 | 55.0% | 0.445 | 13 |
| PCA-2 | −0.009 | 55.4% | 0.302 | 7 |
| PCA-3 | −0.009 | 55.9% | 0.264 | 14 |

Removing the market cut the average pairwise correlation from **0.285 to 0.054**, a drop of about 81%.

![Pairwise correlations before and after removing the market](figures/factor_adjusted_distribution.png)

The raw distribution (blue) sits well to the right of zero. The market-adjusted distribution (orange) is centered close to zero. The right-hand tail is the part that matters for the networks.

---

# Result 2: 60% of the Strongest Edges Survived

Of the 47 raw Extreme edges, **28 (60%) are still in the top 1% after removing the market**. The other 19 were not as special as they looked.

| Version | Raw Extreme edges surviving |
|---|---:|
| Market (QQQ) | 28 of 47 (60%) |
| PCA-1 | 28 of 47 (60%) |
| PCA-2 | 32 of 47 (68%) |
| PCA-3 | 27 of 47 (57%) |

Survivors include all the "self-explanatory" pairs from Part 1:

* ADP–PAYX: 0.856 → 0.836 (barely moved)
* KLAC–LRCX: 0.913 → 0.763
* CDNS–SNPS: 0.725 → 0.607
* AEP–EXC–XEL, CHTR–CMCSA, BKR–FANG

The lost edges were mostly **links between different kinds of semiconductor companies** (e.g. ADI–KLAC, LRCX–NXPI, KLAC–QCOM), plus the edges involving ARM, AVGO, and NVDA, and two of the three cybersecurity edges (CRWD–PANW, PANW–ZS).

<table>
<tr>
<td><img src="figures/extreme_network_raw.png" alt="Raw Extreme network"></td>
<td><img src="figures/extreme_network_market_adjusted.png" alt="Market-adjusted Extreme network"></td>
</tr>
</table>

---

# Result 3: The Semiconductor Ecosystem Split in Two

In Part 1, the Extreme network had one 15-company semiconductor component. After removing the market, it splits into two groups that look like two different businesses:

**Analog / microcontrollers / connectivity (7):**
ADI, GFS, MCHP, NXPI, ON, QCOM, TXN

**Equipment and memory (5):**
AMAT, ASML, KLAC, LRCX, MU

The edges *within* each group survive. The edges *between* the groups mostly don't.

These are technically different kinds of businesses. The first group sells chips into cars, factories, and phones. The second sells the machines that make chips (plus Micron's memory). It looks like what held them together in Part 1 was partly that they are all high-beta stocks that move a lot with the market. Once that shared movement is removed, the two sub-industries separate.

This holds across versions: the five analog companies (ADI, MCHP, NXPI, ON, TXN) stay together in every adjusted version, and the equipment group stays together in all of them too.

---

# Result 4: Hidden Structures

Removing the market revealed groups that raw correlation had hidden ✨💃✨:

* **Consumer staples:** KDP, KHC, MDLZ, PEP
* **Biotech / pharma:** AMGN, AZN, BIIB, REGN
* **A bigger business-services group:** ADP, CTAS, LIN, ORLY, PAYX, ROP, VRSK

The raw correlations of these companies with *everything* are low, so they never reached the top 1% when ranked against the semiconductor pairs. Once the market is removed, how much they move with each other stands out.

There is a catch with that last group, though. Under PCA-1, utilities, staples, and business services all merge into one 13-node component. That looks less like an industry and more like defensive stocks. When PC2 is also removed, the group shrinks back to ADP, CTAS, PAYX, VRSK. So PC2 seems to be roughly "defensive vs. high-growth."

---

# Result 5: The AI Names, Revisited

In the market-adjusted Extreme network, **every AI name I tracked has degree 0**: NVDA, AVGO, AMD, MSFT, GOOGL, META, AMZN, and PLTR. Several of them are high-beta stocks (PLTR, AMD, and NVDA are all in the top 10 betas vs. QQQ). So a lot of what connected them in the raw network was their shared sensitivity to the market.

| Pair | Raw | Market (QQQ) | PCA-1 |
|---|---:|---:|---:|
| AVGO–NVDA | 0.729 | 0.329 | 0.550 |
| META–MSFT | 0.656 | 0.253 | 0.406 |
| AMD–NVDA | 0.596 | 0.058 | 0.308 |
| GOOGL–MSFT | 0.424 | −0.132 | 0.111 |

### A Caveat About QQQ and Mega-Caps

The two "market" versions agree on almost everything except the mega-caps. For example, GOOGL–MSFT is −0.132 with QQQ but 0.111 with PCA-1.

I think the reason is that QQQ is partly made of these companies. NVDA, MSFT, GOOGL, META, AMZN, and AVGO are a large share of QQQ, so regressing them on QQQ also removes part of their own movement. That can push their residuals artificially apart. PCA-1 is built from standardized returns of all 97 companies, so no single company dominates it. For the mega-caps, I trust PCA-1 more.

Under PCA-1, AVGO–NVDA (0.550) still makes the Extreme network as its own pair, and AMD–NVDA (0.308) is still in the 96th percentile. So the AMD–NVDA relationship is weaker than its raw number suggested, but it isn't zero.

### A Tentative (but Interesting) Cluster Under PCA-3

After removing three components, a 14-company component appears that mixes:

* chips (NVDA, AVGO, AMAT, ASML, KLAC, LRCX, MU)
* hyperscalers (MSFT, META)
* power companies (AEP, CEG, EXC, XEL)
* plus CTAS

Edges like MSFT–NVDA, AVGO–EXC, EXC–LRCX, and AEP–CEG show up here.

That looks a lot like an AI data-center buildout theme: the chips, the companies buying them, and the utilities powering the data centers. If that holds up, it's the closest thing to an answer to my original question from Part 1: an AI ecosystem *does* emerge, but only after removing the market and broad style factors, and it includes power companies, which I never would have put on my list but really should have. 

That said, almost every one of those edges is flagged as near-threshold (see the next section). PCA-3 is estimated on the same year it's tested on, and CTAS being in there is hard to explain. So this is just a hypothesis.

---

# Result 6: The Part 2 Anomalies

Part 2 found 26 cross-industry pairs that were unusually correlated relative to their industries. Twenty-five of them can still be computed with the current population. Here is how many stay in the top 5% of industry-adjusted scores:

| Version | Part 2 anomalies still in the top 5% |
|---|---:|
| Raw | 25 of 25 |
| Market (QQQ) | 18 of 25 |
| PCA-1 | 16 of 25 |
| PCA-2 | 9 of 25 |
| PCA-3 | 4 of 25 |

The two standouts from Part 2 went opposite ways:

* **AMZN–GEHC did not survive:** Its industry-adjusted score went from the 99th percentile to roughly the median (z = 2.02 → −0.02). 
* **CDW–FTNT survived:** It stays in the 90th percentile with QQQ and the 96th percentile under PCA-3. This is the pair with a direct channel-partner relationship.

### The ADP Mystery, Probably Solved

In Part 2, ADP kept showing up as anomalously correlated with its customers (XEL, CCEP, MNST, ORLY, TMUS, COST), and I guessed it was a coincidence.

Part 3 gives a better explanation. ADP–XEL *survives* removing the market (98.7th percentile), but falls to the 67th percentile once PC2 is removed and to the 23rd under PCA-3. Combined with Result 4, I think ADP and those customers are mostly defensive stocks that move together on defensive-vs-growth days. I just hadn't learnt about defensive stocks yet when I started this project. 

---

# How Sure Are These Edges?

With 249 trading days, every correlation has sampling error. Using the Fisher z-transform, I computed a 95% interval for each Extreme edge and flagged edges whose interval reaches below the Extreme threshold. Those edges could plausibly fall on the other side of the cutoff with a different sample.

| Version | Extreme edges | Near-threshold |
|---|---:|---:|
| Raw | 47 | 26 |
| Market (QQQ) | 47 | 21 |

So in both versions, roughly half of the Extreme edges are near the line. The strongest edges (ADP–PAYX, KLAC–LRCX, AMAT–KLAC, the analog-chip core) are solid. The edges right at the threshold shouldn't be read individually. This is also a limitation of Parts 1 and 2 that I didn't account for at the time.

---

# What Did I Learn From Part 3?

* **About 81% of the average correlation was the market** (0.285 → 0.054).
* **40% of the strongest edges were mostly market** (19 of 47 didn't survive).
* **The semiconductor ecosystem is really two ecosystems**, analog chips and chip equipment.
* **Defensive companies hide in raw networks.** Staples, biotech, and business services only appear after the market is removed.
* **Possible AI Cluster.** A possible AI-buildout cluster (chips + hyperscalers + power) appears under PCA-3, but the evidence is weak.

---

# Future Work

### Stocks as Genes

I had a dream last week about this and that's what made me circle back to this project. Biologists who study gene expression face a similar problem: thousands of genes, noisy measurements, and the goal of finding groups that move together. Their toolkit (co-expression networks, module detection, null models, stability checks) maps surprisingly well onto stock returns.

The plan:

1. **Factor-adjusted co-expression network:** start from PCA-residual returns, like this part does.
2. **Community detection instead of thresholds:** find modules with a method like Leiden or WGCNA-style clustering instead of picking a cutoff.
3. **Null models and bootstrap stability:** check which modules are stronger than chance and which survive resampling the trading days.
4. **Trade it:** a mean-reversion strategy that trades each stock against its own module, backtested walk-forward (only past data at each date) and after transaction costs.
5. **Benchmark:** compare against the standard PCA-residual stat-arb strategy (Avellaneda–Lee). Does the biology version actually beat it?

### Other Things I'd Do

* **Longer windows and rolling networks:** redo the 5- and 10-year analyses from Part 2 with factor adjustment, and track how clusters change over time instead of using one snapshot.
* **Better data:** historical index membership and CRSP data through WRDS, to deal with survivorship bias and delisted companies like EA and WBD.
* **Test the AI-buildout cluster properly:** see whether chips, hyperscalers, and power utilities really co-move after factor adjustment in an out-of-sample year.
* **Finish validating the Extreme edges:** Part 2 only manually checked 20 of the 49 raw Extreme edges.

But first, I need to focus on passing my quals and my primary research. I'll circle back in 2027. 

---

# Limitations

* One year of daily returns (249 days); about half of the Extreme edges are near-threshold.
* Population is the 2025 Nasdaq-100, now 97 companies after the EA and WBD delistings.
* QQQ contains the mega-caps it's being used to adjust, which distorts their market-model residuals.
* PCA components are estimated on the same year they're applied to (fine for description, not for trading).
* PCA can remove real industry structure along with style factors.
* Industry labels come from `yfinance` and are imperfect.
* Correlation does not establish causation, and residual correlation doesn't either.
* Network structure still depends on the chosen threshold.

---

# Files

* `src/factor_adjusted.py`: the whole of Part 3
* `outputs/factor_adjusted_output.txt`: full printed output
* `outputs/factor_adjusted_summary.csv`: summary by version
* `outputs/factor_adjusted_extreme_edges.csv`: Extreme edges for every version, with 95% intervals
* `outputs/factor_adjusted_edge_survival.csv`: which raw Extreme edges survived, were lost, or are new
* `outputs/factor_adjusted_tracked_pairs.csv`: pairs discussed in Parts 1 and 2
* `outputs/factor_adjusted_anomalies.csv`: Part 2 anomalies under each version
* `outputs/factor_adjusted_ai_names.csv`: degree and neighbors of the AI names
* `outputs/market_betas.csv`, `outputs/pca_explained_variance.csv`
* `figures/factor_adjusted_distribution.png`, `figures/extreme_network_raw.png`, `figures/extreme_network_market_adjusted.png`