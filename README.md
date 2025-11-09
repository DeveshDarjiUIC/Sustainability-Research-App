# Illinois County Sustainability Maturity & Recommendation Engine

This project analyzes the sustainability maturity of Illinois counties by leveraging Retrieval-Augmented Generation (RAG) to score official reports. It then uses K-means clustering on demographic and financial data to provide actionable recommendations for municipalities seeking to enhance their sustainability initiatives.

## Overview

The primary goal of this project is to create a data-driven framework to:
1.  **Objectively Score:** Quantify a county's "sustainability maturity" by analyzing its published reports using a RAG-based LLM pipeline.
2.  **Identify Peer Groups:** Cluster counties using K-means based on their demographic, financial, and other key metrics.
3.  **Generate Recommendations:** Provide targeted advice to lower-maturity counties by identifying successful strategies from high-performing "peer" counties within their same cluster.

## Workflow

The project methodology is broken down into the following key stages:



### 1. Data Collection
* **Sustainability Reports:** A corpus of official sustainability reports and related documents was gathered from various Illinois county websites.
* **County-Level Metrics:** A corresponding dataset was compiled for all counties, including:
    * **Demographic Data:** Population size, density, median income, etc.
    * **Financial Data:** County budget, tax revenue, public spending, etc.
    * **Other Metrics:** [Specify any other metrics you used, e.g., geographic size, primary industries]

### 2. RAG-Based Scoring
To move beyond simple keyword analysis, a **Retrieval-Augmented Generation (RAG)** pipeline was implemented.
* **Vector Database:** All collected reports were processed, chunked, and stored in a vector database to serve as the "knowledge base."
* **Score Generation:** A large language model (LLM) was prompted to evaluate each county's documentation. The RAG pipeline retrieved the most relevant sections from the reports to "ground" the model's assessment, resulting in a quantifiable "Sustainability Maturity Score" for each county.

### 3. K-Means Clustering
Once the scores were generated, they were added as a new feature to the county-level metrics dataset. The K-means algorithm was then applied to this dataset to partition the counties into distinct clusters.

The goal was to group counties with similar underlying characteristics (e.g., "urban, high-resource," "rural, low-resource") so that future recommendations could be compared fairly.

### 4. Recommendation Generation
By analyzing the clusters, we can identify high-performing (high-maturity score) counties within each group. The strategies and initiatives detailed in their reports serve as a practical, context-aware "blueprint" for lower-scoring counties *in the same cluster*.

**Example:** A recommendation for a low-resource, rural county would be based on a successful program from a high-performing, low-resource, rural county—not from a high-resource urban center like Cook County.

## Results
* A final ranked list of Illinois counties based on their generated sustainability scores.
* A detailed analysis of the `K` clusters identified, including their defining characteristics.
* A set of generated recommendations tailored to each cluster.

*(You can link to your analysis notebooks, final reports, or visualizations here)*

## How to Run This Project

### Prerequisites
* Python 3.9+
* Jupyter Notebook (or your preferred IDE)
* [Any specific database, e.g., ChromaDB, Pinecone]
* [An LLM API Key, e.g., OpenAI, Anthropic]




## Future Work
* Integrate a web-based dashboard for visualizing the county rankings and cluster data.
* Expand the analysis to include more states or a national dataset.
* Automate the report-gathering process with a web scraping pipeline.



## Acknowledgments
* [Any data sources you want to credit, e.g., U.S. Census Bureau]
* [Any libraries or tools that were critical to your success]
