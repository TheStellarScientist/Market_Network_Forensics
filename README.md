# Market Network Forensics

This is just a fun little project I did mostly out of curiosity.

The basic question was: "Can we recover real economic structure using only the relationships between stock returns, without telling the network what the companies actually do?"

I used 2025 daily returns for the Nasdaq-100 to construct correlation networks at several levels of relationship strength. The networks ended up recovering recognizable economic structures on their own, including a particularly strong semiconductor ecosystem, utilities, cybersecurity companies, direct competitors, and other economically related groups.

From there, the project turned into something closer to a mini investigation. I looked at some of the strongest relationships manually, searched for unusual cross-industry correlations, and compared the network across one-, five-, and ten-year observation windows. That produced a few fun findings, including real commercial relationships hidden behind seemingly unrelated industry classifications and an interesting change in the AMD–NVDA relationship around the 2023 AI boom.

## Forensic Network Science

I'm calling the general approach forensic network science. It's what I use for my research on matrix multiplication algorithms (I'm a grad student) and I wanted to apply it to different industries and problems. 

The idea is:

$$
\text{population}
\rightarrow
\text{relationships}
\rightarrow
\text{network}
\rightarrow
\text{structure}
\rightarrow
\text{anomalies}
\rightarrow
\text{possible mechanisms}
$$

It's like getting a completely filled out sudoku board and then trying to figure out the rules of the game. 

## Project Notes

This is a fun scavenger hunt, not a trading strategy or an attempt to establish causal relationships between stock returns.

The investigation is split into two reports:

* **Hidden Structure in the Nasdaq-100 #1** — building the network, exploring different correlation regimes, and forming the initial hypotheses.
* **Hidden Structure in the Nasdaq-100 #2** — validating relationships, investigating anomalies, and comparing the network across one-, five-, and ten-year time horizons.

Mostly I wanted to see if it would work and it did. So I'm going to apply it to different projects when I have time. I have so many ideas. 
