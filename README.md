# YouTube Trending Network Analysis

##  Project Overview
This project applies **Network Science** and **Graph Theory** to analyze the ecosystem of YouTube Trending Videos. By examining when and how channels trend together within the same time period and category, we construct a channel co-trending network to uncover the hidden structural mechanics of digital attention.

> **Core Concept:** > Two YouTube channels are connected by an edge if their videos appear together in the trending dataset within the same time window and content category.

The project evaluates network topology, statistical distributions, community structures, centrality measures, and compares empirical results against theoretical graph models.

---

##  Project Objectives
The pipeline is designed to answer several key research questions:
* **Influence:** Which YouTube channels act as structural hubs and major information brokers?
* **Topology:** Does the YouTube trending network follow a scale-free distribution ($P(k) \sim k^{-\alpha}$)?
* **Connectivity:** Does the network exhibit small-world characteristics?
* **Segmentation:** How do channels cluster into distinct, specialized communities?
* **Validation:** How does the empirical YouTube network compare with classic synthetic network models (ER, BA, WS)?

---

##  Dataset Description
The analysis utilizes the **YouTube Trending Videos Dataset** covering two major regions:
* 🇺🇸 **United States (US)**
* 🇬🇧 **Great Britain (GB)**

### Key Features Used:
* `video_title`, `channel_title`, `category_id`
* `trending_date`
* Engagement metrics: `views`, `likes`, `comment_count`

---

##  Network Construction
The system models the data as an undirected, weighted graph $G = (V, E)$, defined by:
* **Vertices ($V$):** Unique YouTube channels.
* **Edges ($E$):** Co-trending relationships between two channels.
* **Edge Weight ($W_{uv}$):** The frequency of co-occurring trending events between channel $u$ and channel $v$.

To filter out noise and weak statistical co-occurrences, an edge threshold is enforced:
$$\text{weight}(u, v) \ge 2$$

---

##  Technologies Used
* **Language:** Python 3.x
* **Data Engineering:** `pandas`, `numpy`
* **Network Science:** `networkx`, `python-louvain`
* **Statistical Modeling:** `powerlaw`
* **Visualization:** `matplotlib`, `seaborn`, `pyvis` (Interactive HTML graphs)

---

##  Project Structure
```text
YOUTUBE_TRENDING/
│
├── data/
│   ├── US.csv
│   └── GB.csv
│
├── src/
│   ├── loader.py          # Data ingestion & pre-processing
│   ├── graph_builder.py   # Edge filtering & Graph instantiation
│   ├── metrics.py         # Topological, powerlaw & modularity calculations
│   └── visualization.py   # Matplotlib, Seaborn & PyVis layouts
│
├── output/
│   ├── figures/           # Distribution and model comparison plots
│   ├── graphs/            # Exported GraphML & Interactive HTML files
│   ├── metrics/           # Raw JSON metadata
│   └── tables/            # Centrality rankings (.csv)
│
├── main.py                # Pipeline execution entry point
└── README.md