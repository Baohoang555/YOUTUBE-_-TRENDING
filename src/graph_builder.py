import re
from collections import Counter
from itertools import combinations
from pathlib import Path
 
import networkx as nx
import pandas as pd
_INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
 
 
def build_graph(
    df: pd.DataFrame,
    weight_threshold: int = 1,
    include_isolated_nodes: bool = False,
) -> nx.Graph:
    G = nx.Graph()
    print("Đang gom nhóm dữ liệu theo ngày và phân khúc nội dung...")
    grouped = df.groupby(["trending_date", "category_name"])["channel_title"].apply(set)
 
    print("Đang tính toán các cặp co-trending (tạo các clique)...")
    edge_counter = Counter()
 
    for channels in grouped:
        if len(channels) > 1:
            # Sắp xếp để đảm bảo cặp (A, B) và (B, A) được tính là một
            sorted_channels = sorted(channels)
            for u, v in combinations(sorted_channels, 2):
                edge_counter[(u, v)] += 1
 
    print(f"Đang xây dựng đồ thị NetworkX (áp dụng ngưỡng weight >= {weight_threshold})...")
    for (u, v), weight in edge_counter.items():
        if weight >= weight_threshold:
            G.add_edge(u, v, weight=weight)
 
    if include_isolated_nodes:
        G.add_nodes_from(df["channel_title"].unique())
 
    return G
 
 
def _sanitize_for_graphml(G: nx.Graph) -> nx.Graph:
    mapping = {node: _INVALID_XML_CHARS.sub("", str(node)) for node in G.nodes()}
    return nx.relabel_nodes(G, mapping)
 
 
def save_graph(G: nx.Graph, country: str, output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{country}_graph.graphml"
 
    G_clean = _sanitize_for_graphml(G)
    nx.write_graphml(G_clean, out_path)
    return out_path
 
 
def load_graph(country: str, output_dir: Path) -> nx.Graph:
    graph_path = Path(output_dir) / f"{country}_graph.graphml"
    if not graph_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {graph_path}. Hãy chạy build_graph() + save_graph() trước."
        )
    return nx.read_graphml(graph_path)
 
 
if __name__ == "__main__":
    try:
        from loader import load_and_clean
    except ImportError:
        from src.loader import load_and_clean
 
    try:
        df_us = load_and_clean("US")
        G_us = build_graph(df_us, weight_threshold=1)
        print(f"[US Graph] Số lượng Nodes: {G_us.number_of_nodes():,}")
        print(f"[US Graph] Số lượng Edges: {G_us.number_of_edges():,}")
    except Exception as e:
        print(f"Lỗi khi chạy thử nghiệm: {e}")