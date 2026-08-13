# Hidden Structure in the Nasdaq-100 #1

> Note: This is an exploratory project investigating whether meaningful economic structure can be recovered from stock-return relationships without explicitly telling the network what industries, sectors, or themes the companies belong to.

> This README is being maintained as a research diary rather than a retrospective report. Some hypotheses below will probably turn out to be wrong. If they do, I intend to leave them here and document what changed my mind.

## Research Question

The original question was:

**Does an AI-related ecosystem emerge from the return network without explicitly telling the algorithm what an "AI company" is?**

More generally, I want to know how much hidden economic structure can be reconstructed using only relationships between company returns.

The basic idea is:

$$
\text{daily returns}
\rightarrow
\text{pairwise relationships}
\rightarrow
\text{network}
\rightarrow
\text{communities / bridges / anomalies}
\rightarrow
\text{possible economic mechanisms}.
$$

This is intended as an exercise in forensic network science rather than a return-prediction project.


## Pilot Investigation

I started with a deliberately selected sample of 10 companies before attempting the full Nasdaq-100.

The sample contained companies I expected to be near the center of AI, companies somewhat adjacent to AI, and two companies deliberately chosen as controls outside that ecosystem.

The sample was:

Companies in the center of AI:
1. NVDA - Nvidia (GPUs/compute)
2. MSFT - Microsoft (OpenAI stake, Azure AI)
3. GOOGL - Alphabet (DeepMind, Gemini, TPUs)
4. AVGO - Broadcom (AI networking/custom silicon)
5. AMD - Advanced Micro Devices (AI Chips, Nvidia's rival)

Companies on the edge of AI:
1. ORCL - Oracle (Stargate partnership, GPU deals)
2. META - Meta (Heavy on AI but it's just social media)
3. PLTR - Palantir (AI/data analytics)

Companies removed from AI:
1. PEP - PepsiCo (Drinks, should be an outlier)
2. COST - Costco (Retail, second outlier)

The point of this stage was partly methodological and partly to learn the Python workflow on a small dataset before scaling it.

I downloaded 2025 daily price data with `yfinance`, extracted closing prices, calculated daily percentage returns, and constructed the pairwise Pearson correlation matrix.

There are

$$
\binom{10}{2}=45
$$

unique pairwise relationships in the pilot.

### There Was Definitely Structure

The strongest relationships included:

* AVGO–NVDA: 0.729
* META–MSFT: 0.656
* MSFT–NVDA: 0.641
* AMD–NVDA: 0.596
* AVGO–ORCL: 0.588
* NVDA–PLTR: 0.575

Meanwhile, PEP repeatedly appeared among the weakest relationships.

This was encouraging because the return data appeared capable of recovering at least some of the structure I had expected.

However, GOOGL became much more interesting once I started constructing networks.


## The GOOGL Threshold Problem

My first network used an arbitrary correlation threshold of 0.5.

At that threshold, NVDA had degree 6 while GOOGL had degree 1.

Initially that makes GOOGL look like it was on the side.

But its relationships were:

* AVGO: 0.506
* AMD: 0.488
* NVDA: 0.484
* META: 0.443
* MSFT: 0.424
* PLTR: 0.418
* ORCL: 0.282
* COST: 0.129
* PEP: -0.088

So the apparent isolation was partly an artifact of placing the
threshold almost exactly between several of its relationships.

I checked the threshold sensitivity right after that:

| Threshold | Edges | NVDA Degree | GOOGL Degree |
|---|---:|---:|---:|
| 0.3 | 28 | 7 | 6 |
| 0.4 | 23 | 7 | 6 |
| 0.5 | 13 | 6 | 1 |
| 0.6 | 3 | 2 | 0 |
| 0.7 | 1 | 1 | 0 |

The all-node sensitivity analysis showed the same problem. Network topology changes *a lot* as the threshold moves.

This convinced me to use multiple thresholds and just have multiple regimes.

---

# Full Nasdaq-100 Investigation

## Population

The full investigation uses the Nasdaq-100 population at the beginning
of 2025 rather than the current index membership.

There were initially 101 securities in the population because Alphabet
was represented by both GOOG and GOOGL.

### ANSS

`yfinance` failed to retrieve ANSS:

> possibly delisted; no timezone found

All 250 observations were missing. This was likely because ANSYS, Inc. was acquired by Synopsys on July 17, 2025. 

That left 100 usable securities.

### GOOG vs GOOGL

GOOG and GOOGL represent two share classes of the same underlying company.

Their 2025 daily-return correlation was:

$$
r=0.9980.
$$

Because the intended unit of analysis is the *company*, including both would give Alphabet two nearly identical nodes. So I dumped GOOG and just kept GOOGL.

The final analysis population contains:

$$
\boxed{99\text{ companies}}.
$$

The return matrix contains 249 daily returns for each company.

## Full Correlation Network

With 99 companies there are:

$$
\binom{99}{2}=4851
$$

unique pairwise relationships.

The strongest relationships were immediately suspicious.

### Strongest Relationships

The top relationships included:

* KLAC–LRCX: 0.913
* AMAT–KLAC: 0.893
* AMAT–LRCX: 0.873
* ADI–MCHP: 0.859
* MCHP–NXPI: 0.859
* ADP–PAYX: 0.856
* ADI–NXPI: 0.848
* ADI–TXN: 0.836
* ASML–KLAC: 0.820
* LRCX–MU: 0.815

Nine of the ten strongest relationships appear to involve semiconductor-related companies.

The exception, ADP–PAYX, is also interesting because the companies appear to occupy closely related economic territory.

This was the first sign that my idea held merit! ✨💃✨

## Correlation Distribution

Across all 4,851 relationships:

* Mean: 0.2817
* Standard deviation: 0.1726
* Minimum: -0.2315
* 25th percentile: 0.1661
* Median: 0.2917
* 75th percentile: 0.4023
* Maximum: 0.9129

Higher empirical quantiles were:

* 90th percentile: 0.4888
* 95th percentile: 0.5428
* 99th percentile: 0.6751

Interestingly, the arbitrary 0.5 threshold from the pilot happened to fall near the 90th percentile of the full distribution. I still decided having multiple thresholds was more interesting though. I have histogram showing the data above below. 

<img width="1979" height="1179" alt="full_correlation_distribution" src="https://github.com/user-attachments/assets/9bda303d-fdd2-4668-83bf-ab19302dccf5" />

---

# Four Network Regimes

The regimes are:

* **Broad:** top 25% of relationships
* **Strong:** top 10%
* **Very Strong:** top 5%
* **Extreme:** top 1%

## Broad Network

Threshold: 0.4023

* Total nodes: 99
* Active nodes: 95
* Isolates: 4
* Edges: 1,213
* Nontrivial connected components: 1
* Largest component: 95 nodes

At this level almost every active company belongs to one connected structure.

This regime only captures broad market/economic connectivity and doesn't separate the population into components.

## Strong Network

Threshold: 0.4888

* Total nodes: 99
* Active nodes: 82
* Isolates: 17
* Edges: 486
* Nontrivial connected components: 5
* Largest component: 69 nodes

Fragmentation started here but the majority of active companies still belong to one large blob component.

## Very Strong Network

Threshold: 0.5428

* Total nodes: 99
* Active nodes: 70
* Isolates: 29
* Edges: 243
* Nontrivial connected components: 7
* Largest component: 50 nodes

The largest component still contains many of the companies that motivated the original AI question, including:

* AMD
* AMZN
* AVGO
* GOOGL
* META
* MSFT
* NVDA
* PLTR

---

# The Extreme Network

Threshold: 0.6751

This retains only approximately the strongest 1% of all observed relationships.

* Total nodes: 99
* Active nodes: 30
* Isolates: 69
* Edges: 49
* Nontrivial connected components: 7
* Largest component: 15 nodes

The network changes drastically between the Very Strong and Extreme regimes.

The largest component shrinks from 50 nodes to 15.

And the composition of the surviving component is highly suspicious! 

## Component 1 — 15 Nodes

* ADI
* AMAT
* ARM
* ASML
* AVGO
* GFS
* KLAC
* LRCX
* MCHP
* MU
* NVDA
* NXPI
* ON
* QCOM
* TXN

This appears to be a semiconductor ecosystem. And the network arrived at this structure using only 2025 return relationships!

## Other Extreme Components

The remaining nontrivial components are also economically interpretable.

### Component 2 — Commercial / Business Services

**ADP, CTAS, PAYX**

ADP and PAYX are direct competitors in payroll processing and related workforce services.

CTAS (Cintas) is not a direct payroll competitor but it provides workplace services such as uniforms and facility products.

I suspect the common structure might actually reflect business employment and workplace activity rather than just one business "type".

### Component 3 — Electric Utilities

**AEP, EXC, XEL**

These companies are all in the electric utility industry. I think this is self explanatory. 

### Component 4 — Cybersecurity

**CRWD, PANW, ZS**

These companies operate in cybersecurity software and compete across areas including endpoint, network, and cloud security. Also self explanatory. 

### Component 5 — Energy (Oil)

**BKR, FANG**

Both companies belong to the broader energy sector, but occupy different parts of it like with Component 2. 

Diamondback Energy (FANG) is an independent oil and gas exploration and production company. Baker Hughes (BKR) provides oilfield services, equipment, and technology used in oil and gas development and production.

I think the correlation may reflect shared exposure to the same underlying energy-market conditions with this group.

### Component 6 — Electronic Design Automation

**CDNS, SNPS**

Cadence Design Systems and Synopsys are direct competitors in electronic design automation (EDA) software and semiconductor design tools.

Interestingly enough, this pair forms a separate Extreme component from the larger 15-node semiconductor component despite being deeply connected to the semiconductor industry.

### Component 7 — Cable / Telecom

**CHTR, CMCSA**

Charter Communications and Comcast are direct competitors in cable and telecommunications services.

It surprised me they were on the list at all because I forgot some people still watch cable. 

## Initial Pattern

The Extreme components clearly represent different types of economic relationships.

So far, they appear to include at least:

1. **Direct competitors** — e.g. CDNS–SNPS and CHTR–CMCSA
2. **Industry peers / shared exposure** — e.g. AEP–EXC–XEL
3. **Related but different positions in the same economic system** —
   e.g. BKR–FANG
4. **Broader business-environment exposure** — potentially
   ADP–CTAS–PAYX

---
# What Happened to the AI Cluster?

The original question assumed that something resembling an AI ecosystem might emerge.

But here's what showed up:

At the Very Strong regime, companies such as MSFT, GOOGL, META, AMZN, PLTR, AMD, NVDA, and AVGO remain inside the largest component.

At the Extreme regime, most of those companies flat out disappear. NVDA and AVGO remain inside the 15-node semiconductor component but MSFT, GOOGL, META, AMZN, PLTR, and AMD do not.

This suggests that "AI" may not behave as a single homogeneous economic community in the return network.

One possibility is that platform/application companies are competitors with highly diversified businesses, while the semiconductor ecosystem shares tighter underlying economic exposures. But that's just a hypothesis. 

---

# NVDA vs AMD Detour

One result I didn't see coming was the difference between NVDA and AMD at the Extreme threshold.

At the 99th-percentile regime:

$$
k_{\mathrm{NVDA}}=2
$$

while

$$
k_{\mathrm{AMD}}=0.
$$

NVDA remains inside the dominant 15-company semiconductor component, while AMD becomes isolated.

This is interesting because NVDA and AMD are normally discussed as competitors.

However, product-market competition clearly does not necessarily imply that two companies occupy the same position in a broader economic network.

My current suspicion is that NVDA may be more structurally integrated with the semiconductor ecosystem represented by this return network, while AMD occupies a different position despite competing with NVDA in some product markets.

Essentially, maybe AMD is a fake competitor. But that's not testable so don't quote me on that. 

What I *can* test is if NVDA is more structurally integrated with the broader semiconductor ecosystem than AMD, based on the persistence and strength of its return-network relationships with semiconductor companies. External evidence and additional network metrics will be needed to evaluate this.

---

# Pre-Validation Hypotheses

>Note: Everything in this section was recorded before systematically investigating external evidence about the 49 Extreme relationships. The purpose of freezing these hypotheses now is so my thought process remains visible.

## Hypothesis 1 — Extreme Edges Reflect Economic Structure

The strongest return relationships will disproportionately correspond to shared economic exposures rather than random company pairs.

## Hypothesis 2 — Semiconductor Ecosystem

The 15-node Extreme component represents a semiconductor economic ecosystem rather than merely a generic technology or AI cluster.

## Hypothesis 3 — AI Is Cross-Community

AI-related companies may participate in a broader ecosystem without forming a single dense community themselves.

Platform and application companies may connect to different portions of the underlying infrastructure network.

## Hypothesis 4 — Direct Relationships

Some Extreme edges will correspond to direct relationships such as:

* supplier/customer relationships
* partnerships
* direct competition
* shared production dependencies

## Hypothesis 5 — Shared Exposure Without Direct Connection

Other Extreme relationships may involve companies with no important direct relationship but strong exposure to the same industry, customers, supply chains, macroeconomic conditions, or other common factors.

## Hypothesis 6 — NVDA and AMD Occupy Different Structural Positions

See above section please. 

---

# Validation — Not Started Yet

The Extreme network contains only 49 edges, which thankfully makes it small enough to investigate every relationship.

The next stage will compare the market-derived network against external evidence about actual company relationships.

Possible relationship categories include:

* supplier/customer
* competitor
* strategic partner
* same industry / shared economic exposure
* other identifiable relationship
* no obvious relationship

The important methodological order is:

$$
\text{discover}
\rightarrow
\text{record hypotheses}
\rightarrow
\text{freeze results}
\rightarrow
\text{research external relationships}
\rightarrow
\text{compare}.
$$

Extra TLC will be paid to Extreme edges with no obvious economic relationship because those are honestly more interesting than the relationships that are easy to explain.

---

# Limitations So Far

This is still an exploratory raw-correlation network.

That means:

* correlations have not yet been adjusted for broad market movements
* sector effects have not been removed
* correlation does not establish causation
* the network represents one year of returns
* ANSS is missing because historical data could not be retrieved from the current source
* network structure depends on the chosen relationship regime
* connected components alone do not identify communities inside the large Broad/Strong/Very Strong components

---

# The Pile for Later

Things I currently want to investigate:

* validation of all 49 Extreme edges
* whether Extreme edges correspond disproportionately to known economic relationships
* unexplained Extreme edges
* supplier/customer relationships
* competitor relationships
* NVDA vs AMD structural differences
* degree persistence across thresholds
* edge persistence across thresholds
* community detection
* betweenness centrality
* market-adjusted return network
* sector-adjusted return network
* null-model comparison
* whether the same structures appear in other years
* whether regime changes in time alter the network topology
