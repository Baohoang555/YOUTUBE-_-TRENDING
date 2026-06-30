 
from pathlib import Path
 
import networkx as nx
import pandas as pd
 
from src.metrics import compute_basic_metrics, fit_power_law
 
 
def _estimate_ba_m(n: int, target_edges: int) -> int:
    if n <= 1:
        return 1
    m_est = round(target_edges / n)
    return max(1, min(m_est, n - 1))
 
 
def _estimate_ws_k(n: int, target_edges: int) -> int:
    avg_degree = 2 * target_edges / n
    k = int(round(avg_degree))
    if k % 2 != 0:
        k += 1
    return max(2, min(k, n - 1))
 
 
def generate_er_graph(n: int, m: int, seed: int = 42) -> nx.Graph:
    return nx.gnm_random_graph(n, m, seed=seed)
 
 
def generate_ba_graph(n: int, m: int, seed: int = 42) -> nx.Graph:
    m_ba = _estimate_ba_m(n, m)
    return nx.barabasi_albert_graph(n, m_ba, seed=seed)
 
 
def generate_ws_graph(n: int, m: int, p: float = 0.1, seed: int = 42) -> nx.Graph:
    k = _estimate_ws_k(n, m)
    return nx.watts_strogatz_graph(n, k, p, seed=seed)
 
 
def compare_with_models(G_real: nx.Graph, ws_p: float = 0.1, seed: int = 42) -> pd.DataFrame:
    n = G_real.number_of_nodes()
    m = G_real.number_of_edges()
 
    graphs = {
        "Real": G_real,
        "Erdos-Renyi (ER)": generate_er_graph(n, m, seed=seed),
        "Barabasi-Albert (BA)": generate_ba_graph(n, m, seed=seed),
        "Watts-Strogatz (WS)": generate_ws_graph(n, m, p=ws_p, seed=seed),
    }
 
    rows = []
    for name, G in graphs.items():
        basic = compute_basic_metrics(G)
        try:
            alpha = fit_power_law(G)["alpha"]
        except Exception:
            alpha = None
 
        rows.append(
            {
                "model": name,
                "num_nodes": basic["num_nodes"],
                "num_edges": basic["num_edges"],
                "average_clustering": basic["average_clustering"],
                "average_shortest_path_length": basic["average_shortest_path_length"],
                "diameter": basic["diameter"],
                "power_law_alpha": alpha,
            }
        )
 
    return pd.DataFrame(rows)
 
 
def compare_countries(metrics_us: dict, metrics_gb: dict) -> pd.DataFrame:
    all_keys = sorted(set(metrics_us.keys()) | set(metrics_gb.keys()))
 
    rows = [
        {"metric": key, "US": metrics_us.get(key), "GB": metrics_gb.get(key)}
        for key in all_keys
    ]
 
    return pd.DataFrame(rows)
 
 
def save_model_comparison_csv(
    df: pd.DataFrame, output_dir: Path, filename: str = "model_comparison.csv"
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    df.to_csv(out_path, index=False)
    return out_path
 
 
if __name__ == "__main__":
    try:
        from loader import load_and_clean
        from graph_builder import build_graph
    except ImportError:
        from src.loader import load_and_clean
        from src.graph_builder import build_graph
 
    try:
        df_us = load_and_clean("US")
        G_us = build_graph(df_us, weight_threshold=1)
 
        comparison_df = compare_with_models(G_us)
        print(comparison_df)
    except Exception as e:
        print(f"Lỗi khi chạy thử nghiệm: {e}")
 