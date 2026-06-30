import re
from collections import Counter
from itertools import combinations
from pathlib import Path
 
import networkx as nx
import pandas as pd
 
# GraphML dùng định dạng XML 1.0, vốn không cho phép một số ký tự control.
# channel_title lấy thẳng từ YouTube API thỉnh thoảng dính ký tự lỗi/control
# char (đặc biệt với dataset US/GB này), nên cần loại trước khi ghi file.
_INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
 
 
def build_graph(
    df: pd.DataFrame,
    weight_threshold: int = 1,
    include_isolated_nodes: bool = False,
) -> nx.Graph:
    """
    Xây dựng Weighted Graph từ DataFrame đã làm sạch.
 
    - Node: Tên channel (channel_title)
    - Edge: Nối giữa 2 channel nếu cùng trending trong cùng 1 category và cùng 1 ngày.
    - Weight: Số lần co-trending tổng cộng.
 
    weight_threshold: Ngưỡng lọc cạnh, chỉ giữ lại cạnh có trọng số >= threshold.
        Tăng giá trị này giúp giảm bớt hiệu ứng "clique" (mọi channel trong
        cùng nhóm ngày+category đều nối với nhau), vốn là giới hạn phương
        pháp đã ghi trong README — nên thử vài giá trị threshold khác nhau
        và so sánh kết quả clustering/small-world.
 
    include_isolated_nodes: Nếu True, thêm tất cả channel xuất hiện trong df
        làm node ngay cả khi channel đó không có cạnh nào đạt threshold
        (degree = 0). Mặc định False, vì các node cô lập không đóng góp gì
        cho hầu hết network metrics (centrality, community, diameter...)
        và sẽ làm sai lệch connected components nếu để mặc định True.
    """
    G = nx.Graph()
 
    print("Đang gom nhóm dữ liệu theo ngày và phân khúc nội dung...")
    # Dùng set() để loại trường hợp 1 channel có nhiều video cùng trending
    # trong 1 ngày cùng 1 category (tránh tự tạo self-loop hoặc đếm trùng)
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
    """
    Loại ký tự control không hợp lệ trong tên node trước khi ghi GraphML.
    Trả về graph mới (không sửa G gốc).
    """
    mapping = {node: _INVALID_XML_CHARS.sub("", str(node)) for node in G.nodes()}
    return nx.relabel_nodes(G, mapping)
 
 
def save_graph(G: nx.Graph, country: str, output_dir: Path) -> Path:
    """
    Lưu đồ thị dưới dạng file GraphML (giữ nguyên thuộc tính weight,
    mở được bằng Gephi/PyVis, và load lại được bằng load_graph()).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{country}_graph.graphml"
 
    G_clean = _sanitize_for_graphml(G)
    nx.write_graphml(G_clean, out_path)
    return out_path
 
 
def load_graph(country: str, output_dir: Path) -> nx.Graph:
    """
    Load lại graph đã lưu từ save_graph(). Dùng ở notebook 02/03 thay vì
    phải build_graph() lại từ đầu mỗi lần.
    """
    graph_path = Path(output_dir) / f"{country}_graph.graphml"
    if not graph_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {graph_path}. Hãy chạy build_graph() + save_graph() trước."
        )
    return nx.read_graphml(graph_path)
 
 
if __name__ == "__main__":
    # Test nhanh module với dữ liệu US đã làm sạch nếu chạy độc lập.
    # Hỗ trợ cả 2 cách chạy: `python src/graph_builder.py` và
    # `python -m src.graph_builder` (từ thư mục gốc dự án).
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