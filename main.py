# ============================================================
# YouTube Trending Network Analysis Pipeline
# ============================================================

import sys
from pathlib import Path


# ============================================================
# Project path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))


# ============================================================
# Internal modules
# ============================================================

from src.loader import (
    load_and_clean,
    save_cleaned
)

from src.graph_builder import (
    build_graph,
    save_graph
)

from src.metrics import (
    compute_basic_metrics,
    compute_small_world_sigma,
    fit_power_law,
    compute_centrality,
    compute_assortativity,
    compute_degree_distribution,
    community_statistics,
    compute_degree_gini,
    save_metrics_json,
    save_centrality_csv
)

from src.visualization import (
    plot_degree_distribution,
    plot_clustering_vs_degree,
    plot_model_comparison,
    generate_interactive_network
)



# ============================================================
# Main pipeline
# ============================================================

def run_pipeline():

    print("=" * 55)
    print(" YOUTUBE TRENDING NETWORK ANALYSIS PIPELINE")
    print("=" * 55)


    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "output"


    # Create folders

    folders = [
        OUTPUT_DIR / "figures",
        OUTPUT_DIR / "graphs",
        OUTPUT_DIR / "tables",
        OUTPUT_DIR / "metrics"
    ]


    for folder in folders:
        folder.mkdir(
            parents=True,
            exist_ok=True
        )


    countries = [
        "US",
        "GB"
    ]


    graphs = {}



    # ========================================================
    # PROCESS EACH COUNTRY
    # ========================================================

    for country in countries:


        print("\n" + "-" * 55)
        print(f" PROCESSING COUNTRY: {country}")
        print("-" * 55)


        try:

            # ------------------------------------------------
            # 1. Load data
            # ------------------------------------------------

            print(
                f"[{country}] Loading dataset..."
            )


            df = load_and_clean(
                country,
                DATA_DIR
            )


            save_cleaned(
                df,
                country,
                OUTPUT_DIR / "tables"
            )



            # ------------------------------------------------
            # 2. Build graph
            # ------------------------------------------------

            print(
                f"[{country}] Building graph..."
            )


            G = build_graph(
                df,
                weight_threshold=2
            )


            graphs[country] = G


            save_graph(
                G,
                country,
                OUTPUT_DIR / "graphs"
            )


            print(
                f"[{country}] "
                f"Nodes={G.number_of_nodes()} "
                f"Edges={G.number_of_edges()}"
            )



            # ------------------------------------------------
            # 3. Network Metrics
            # ------------------------------------------------

            print(
                f"[{country}] Computing network metrics..."
            )


            metrics = {}


            metrics.update(
                compute_basic_metrics(G)
            )


            metrics.update(
                compute_small_world_sigma(G)
            )


            metrics.update(
                fit_power_law(G)
            )


            metrics.update(
                compute_assortativity(G)
            )


            metrics.update(
                compute_degree_distribution(G)
            )


            metrics.update(
                community_statistics(G)
            )


            metrics["degree_gini"] = (
                compute_degree_gini(G)
            )



            save_metrics_json(
                metrics,
                country,
                OUTPUT_DIR / "metrics",
                "network_metrics.json"
            )


            print(
                f"[{country}] Metrics saved"
            )



            # ------------------------------------------------
            # 4. Centrality analysis
            # ------------------------------------------------

            print(
                f"[{country}] Computing PageRank / Centrality..."
            )


            centrality_df = compute_centrality(G)


            save_centrality_csv(
                centrality_df,
                country,
                OUTPUT_DIR / "tables"
            )


            print(
                centrality_df.head(10)
            )



            # ------------------------------------------------
            # 5. Visualization
            # ------------------------------------------------

            print(
                f"[{country}] Creating figures..."
            )


            plot_degree_distribution(
                G,
                country,
                OUTPUT_DIR / "figures"
            )


            plot_clustering_vs_degree(
                G,
                country,
                OUTPUT_DIR / "figures"
            )



            # ------------------------------------------------
            # 6. Interactive graph
            # ------------------------------------------------

            print(
                f"[{country}] Creating PyVis graph..."
            )


            generate_interactive_network(
                G,
                country,
                OUTPUT_DIR / "graphs"
            )



            print(
                f" {country} completed successfully"
            )



        except Exception as e:

            print(
                f" Error processing {country}: {e}"
            )

            continue




    # ========================================================
    # Model comparison
    # ========================================================

    print("\n" + "=" * 55)
    print(" MODEL COMPARISON")
    print("=" * 55)



    comparison_csv = (
        OUTPUT_DIR
        /
        "tables"
        /
        "model_comparison.csv"
    )



    if comparison_csv.exists():

        plot_model_comparison(
            comparison_csv,
            OUTPUT_DIR / "figures"
        )


        print(
            "Model comparison figure generated"
        )


    else:

        print(
            "model_comparison.csv not found"
        )



    print("\n" + "=" * 55)
    print(" PIPELINE FINISHED")
    print("=" * 55)



# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    run_pipeline()