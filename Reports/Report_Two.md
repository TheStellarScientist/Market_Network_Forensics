# Hidden Structure in the Nasdaq-100 #2

> This is the second and final part of my exploratory investigation into whether meaningful economic structure can be recovered from stock-return relationships without explicitly telling the network what industries, sectors, or themes the companies belong to.

The first part constructed a correlation network from 2025 Nasdaq-100 returns and identified several economically interpretable structures, including a large semiconductor ecosystem at the most extreme correlation threshold.

This part asks two slightly different questions:

**Do unusually strong relationships in the network correspond to real economic relationships between companies?**

And:

**Do the structures found in 2025 persist when the observation window is expanded to five and ten years?**

---

# Extreme Network Validation

The 2025 Extreme network contained 49 edges representing approximately the strongest 1% of the 4,851 pairwise correlations.

I originally planned to manually investigate all 49 but I stopped after just 20 edges as all the relationships were predictable.

The investigated edges repeatedly corresponded to things such as:

* direct competitors
* companies in the same industry
* companies exposed to the same economic conditions
* companies occupying different positions within the same supply chain or technological ecosystem
* known technological dependencies

The network was recovering economic structures. Which is exactly what I expected. 

>Note: A separate document containing the manual classifications of the 20 investigated Extreme relationships is available with this directory.

The more interesting question was:

**What happens when two companies correlate much more strongly than we would expect based on their industries?**

---

# Looking for Anomalies

Instead of looking for the highest correlations, I compared each company's relationships against the typical correlations between its industry and other industries.

I focused on cross-industry relationships with correlations between 0.4 and 0.5 and calculated an industry-adjusted anomaly score.

This produced 26 forensic candidates whose correlations were unusually high relative to their respective industry relationships.

Examples included:

* ADP–XEL
* AMZN–GEHC
* ADP–CCEP
* ADP–ORLY
* CDW–FTNT
* ADI–CTAS
* BKR–CDNS
* AXON–NVDA

Unlike the Extreme network, many of these relationships were not immediately obvious from the companies' industry classifications. I manually investigated all 26 and dismissed most of them. But a few did stand out to me.

---

# Standout Relationships

## ADP Customer Relationships

The strangest pattern involved ADP of all companies.

Six ADP relationships appeared among the 26 anomalies:

* ADP–XEL
* ADP–CCEP
* ADP–MNST
* ADP–ORLY
* ADP–TMUS
* ADP–COST

All six companies have or historically had some form of commercial relationship with ADP.

The relationship types vary as some involve payroll services, while others involve narrower employee or benefits services. Costco and T-Mobile have also historically used ADP while moving away from parts of that relationship.

This is interesting because these companies span completely different industries:

* electric utilities
* beverages
* auto parts
* telecommunications
* retail

Their industry classifications provide no obvious reason for ADP to repeatedly appear as an anomalously correlated company.

However, I don't actually think this demonstrates that using ADP causes these companies' stock returns to correlate with ADP. Most large companies use ADP so it's likely just a coincidence. 

---

## Amazon — GE HealthCare

**AMZN–GEHC**

GE HealthCare has a substantial technological relationship with Amazon through AWS, including cloud infrastructure and collaboration involving AI and healthcare applications.

This relationship is invisible if the companies are viewed only through their conventional industry classifications:

*Internet Retail ↔ Medical Devices*

The anomaly screen still identified the pair as unusually correlated relative to those industries.

---

## CDW — Fortinet

**CDW–FTNT**

CDW sells and implements Fortinet products and operates as a Fortinet channel partner.

Again, the industry labels:

*Information Technology Services ↔ Software Infrastructure*

don't explicitly encode the direct commercial relationship between the companies.

---

# Extending the Time Horizon

At this point I considered the project basically finished.

But there was one result from the original 2025 network that bothered me enough to run one more experiment.

## AMD vs NVDA

In the original 2025 Extreme network, NVDA remained inside the semiconductor ecosystem while AMD disappeared entirely.

Their 2025 daily-return correlation was:

$$
r_{\mathrm{AMD,NVDA}}=0.596
$$

That was a surprisingly weak structural relationship given how frequently the companies are discussed as direct competitors.
As I didn't trust only one year of data, I reran the same network analysis over progressively longer observation windows.

The population remained based on the 2025 Nasdaq-100 companies so that the experiment changed the time horizon, rather than simultaneously changing both the population and the time horizon.

Because some companies did not have complete histories, correlations were calculated using available overlapping observations rather than dropping every date containing a missing value. I didn't want to lose 3 years of data because a single company disappeared. 

---

# Five-Year Network: 2021–2025

The five-year return matrix contained 1,255 trading days.

The Extreme threshold was:

$$
r=0.6871
$$

The largest Extreme component contained 13 companies:

* ADI
* AMAT
* AMD
* ASML
* KLAC
* LRCX
* MCHP
* MU
* NVDA
* NXPI
* ON
* QCOM
* TXN

The semiconductor ecosystem therefore survived almost completely intact.

The only difference I cared about is AMD is in the ecosystem.

Its five-year correlation with NVDA was:

$$
r_{\mathrm{AMD,NVDA}}=0.700
$$

That was strong enough to place AMD directly back inside the Extreme semiconductor component.

Several of the smaller structures from 2025 also persisted:

* AEP–EXC–XEL
* ADP–PAYX
* CDNS–SNPS
* CRWD–ZS

A new DDOG–MDB pair also appeared at the Extreme level.

So AMD's isolation in 2025 was not a permanent feature of the broader return network.

---

# Ten-Year Network: 2016–2025

I then expanded the analysis so I ended up getting a ten-year return matrix with 2,514 trading days.

The Extreme threshold became:

$$
r=0.6660
$$

Once again, the largest Extreme component was a semiconductor ecosystem:

* ADI
* AMAT
* ASML
* GFS
* KLAC
* LRCX
* MCHP
* MU
* NXPI
* ON
* TXN

The strongest relationships included:

* AMAT–LRCX: 0.903
* KLAC–LRCX: 0.883
* AMAT–KLAC: 0.869
* ADI–MCHP: 0.838
* ADI–TXN: 0.832

So the semiconductor structure was not just a 2025 phenomenon.

It survived across a decade of returns.

However, **both AMD and NVDA disappeared from the ten-year Extreme semiconductor component**.

This gives the AMD–NVDA result a much more interesting interpretation.

---

# AMD–NVDA Was Regime-Dependent

Across the three observation windows, AMD and NVDA behave differently.

| Window    | AMD–NVDA Relationship   | Extreme Network                               |
| --------- | ----------------------- | --------------------------------------------- |
| 2025      | r = 0.596               | AMD isolated; NVDA remains                    |
| 2021–2025 | r = 0.700               | AMD and NVDA connected                        |
| 2016–2025 | Below Extreme threshold | Neither belongs to Extreme semiconductor core |

The five-year window therefore captures a period when AMD and NVDA became unusually tightly connected in the return network.

The ten-year result suggests this was not always true.

Then in 2025, their correlation weakened again.

So the original 2025 result probably was not telling me that AMD somehow occupies an entirely different economic ecosystem from Nvidia.

Instead, it revealed something about **time**.

Some relationships appear structurally persistent.

Others strengthen and weaken depending on the economic regime being measured.

AMD–NVDA appears to belong to the second category.

---

# The Persistent Semiconductor Core

The comparison across one, five, and ten years also changes how I interpret the semiconductor component itself.

The exact membership changes.

But the underlying structure does not disappear.

Companies such as AMAT, KLAC, LRCX, ADI, MCHP, NXPI, ON, and TXN repeatedly form extremely strong relationships across different observation windows.

This suggests there is a persistent semiconductor core whose return relationships survive substantial changes in the measurement period.

AMD and NVDA are more peripheral to that persistent structure.

Their importance to AI does not necessarily mean their stocks occupy the most stable positions in the broader semiconductor return network.

---

# A Ten-Year Technology Component

The ten-year Extreme network also produced something that did not appear as clearly in the shorter windows.

A separate five-company component emerged:

* AAPL
* ADBE
* GOOGL
* INTU
* MSFT

MSFT sat at the center with degree 4.

Its Extreme relationships included:

* GOOGL–MSFT: 0.705
* ADBE–MSFT: 0.695
* AAPL–MSFT: 0.677
* INTU–MSFT: 0.675

This looks much closer to a persistent large-cap technology/software ecosystem.

Ironically, expanding the observation window produced something closer to the broad technology structure that originally motivated the project.

It still was not an "AI cluster."

But it was another example of economically recognizable structure emerging from return data alone.

---

# What Happened to the Anomalies?

The anomaly results were much less stable than the Extreme network structure.

The five-year analysis produced 33 forensic candidates.

The ten-year analysis produced 35.

But the specific companies appearing at the top changed substantially across observation windows.

The original ADP pattern also weakened.

Only some of the ADP relationships that appeared in the 2025 anomaly set remained unusually strong over longer windows.

That makes me more comfortable treating the original six-company ADP pattern as an interesting coincidence rather than evidence that ADP's customer network was somehow driving stock-return relationships.

This contrast may actually be one of the more useful results of the project:

**The broad economic structures were relatively persistent. The unusual individual cross-industry anomalies were not.**

---

# What Did I Actually Learn?

The original project started with AI.

I wanted to know whether an AI ecosystem would emerge from stock returns without explicitly telling the network what an AI company was.

That isn't really what happened.

Instead, the network repeatedly recovered more traditional economic structures.

The strongest example was the semiconductor ecosystem.

It appeared in the 2025 network.

It remained in the five-year network.

And it remained in the ten-year network.

Several smaller relationships and components also persisted across time.

At the same time, individual companies moved in and out of those structures.

AMD and NVDA were the clearest example.

Their relationship was not permanently weak or permanently strong. It changed depending on the period being measured.

So my final interpretation is:

**Stock-return networks can recover recognizable economic structure without being explicitly given information about company industries or relationships. Some of those structures remain remarkably persistent across different time horizons, while individual edges and peripheral companies can be highly regime-dependent.**

The anomaly investigation also showed that unusual cross-industry correlations can occasionally correspond to real relationships that conventional industry classifications do not encode.

But those anomalies were much less stable across time.

That does not mean any of these relationships caused the observed correlations.

It means there was structure in the noise.

And some of that structure survived ten years.

That's good enough for me.

---

# Final Limitations

This project remains exploratory.

In particular:

* the population is based on the 2025 Nasdaq-100 rather than historical index membership
* companies have different amounts of available trading history in the five- and ten-year analyses
* correlations were calculated using overlapping observations when complete histories were unavailable
* correlations were not adjusted for broad market factors
* sector and style factors may explain some apparent relationships
* industry classifications are imperfect
* anomalous correlation does not imply a direct economic relationship
* direct economic relationships do not imply that those relationships caused the observed correlations
* only 20 of the original 49 Extreme edges were manually validated
* the ADP pattern may be coincidence rather than evidence of a meaningful market mechanism
* network structure still depends on both the chosen threshold and the observation window

A more rigorous project could use factor-adjusted returns, rolling networks, historical index membership, formal null models, and automated relationship validation.

I'm not doing that.

The project is done.
