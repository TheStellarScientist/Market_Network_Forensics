'''
Attempting to build tags and form a dictionary for all 99 companies now.


This was run with: /gpfs/home/guwechue/miniconda3/bin/python src/build_industry_tags.py > outputs/build_industry_tags_output.txt

Well Wishes,
DeDe
'''

import yfinance as yf
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Testing with Nvdia
# ticker = yf.Ticker("NVDA")

# info = ticker.info

# print(info.get("sector"))
# print(info.get("industry"))

# Running for all 99 now.

with open("data/nasdaq100_2025.txt", "r") as file:
    tickers = [
        line.strip()
        for line in file
        if line.strip()
    ]

tickers.remove("ANSS")
tickers.remove("GOOG")

industry_data = []

for ticker in tickers:
    company = yf.Ticker(ticker)
    info = company.info

    result = {
        "Ticker": ticker,
        "Sector": info.get("sector"),
        "Industry": info.get("industry")
    }

    industry_data.append(result)

    print(
        ticker,
        info.get("sector"),
        info.get("industry")
    )

industry_df = pd.DataFrame(industry_data)

industry_df.to_csv(
    "data/company_industries.csv",
    index=False
)

print("\nUnique Industry Labels:")
print(
    industry_df["Industry"]
    .value_counts()
)

print("All Done!")