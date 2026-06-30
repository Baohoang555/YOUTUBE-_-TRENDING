import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import pandas as pd
import powerlaw
from pyvis.network import Network
from pathlib import Path
from typing import Dict, Hashable, cast
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="powerlaw")

def set_seaborn_style():
    """Thiết lập style vẽ đồ thị sạch đẹp, chuyên nghiệp"""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.labelsize"] = 14
    plt.rcParams["axes.titlesize"] = 16

def plot_degree_distribution(G: nx.Graph, country: str, output_dir: Path):
    """Vẽ phân phối bậc dạng Log-Log plot và đường fit Power-law"""
    set_seaborn_style()
    degrees = [d for _, d in G.degree() if d > 0]
    
    fig, ax = plt.subplots()
    
    fit = powerlaw.Fit(degrees, xmin=2, verbose=False)
    
    powerlaw.plot_pdf(degrees, ax=ax, color='b', linestyle='', marker='o', label='Thực tế (Real Data)')
    fit.power_law.plot_pdf(color='r', linestyle='--', ax=ax, label=f'Power-law Fit ($\\alpha$ = {fit.power_law.alpha:.2f})')
    
    ax.set_title(f"[{country}] Phân phối bậc kênh YouTube Trending (Log-Log)")
    ax.set_xlabel("Bậc của Node (Degree $k$)")
    ax.set_ylabel("Xác suất $P(k)$")
    ax.legend()
    
    out_path = Path(output_dir) / "degree_distribution.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    return out_path

def plot_clustering_vs_degree(G: nx.Graph, country: str, output_dir: Path):
    set_seaborn_style()

    nodes = list(G.nodes())

    clustering_dict = cast(
    Dict[Hashable, float],
    nx.clustering(G)
)

    degrees_list = [
        G.degree(node)
        for node in nodes
    ]

    clustering_list = [
        clustering_dict[node]
        for node in nodes
    ]

    df = pd.DataFrame({
        "Degree": degrees_list,
        "Clustering": clustering_list
    })

    avg_clustering = (
        df.groupby("Degree")["Clustering"]
        .mean()
        .reset_index()
    )

    plt.figure()

    sns.scatterplot(
        data=df,
        x="Degree",
        y="Clustering",
        alpha=0.3,
        color="gray",
        label="Từng node"
    )

    sns.lineplot(
        data=avg_clustering,
        x="Degree",
        y="Clustering",
        color="red",
        linewidth=2,
        label="Xu hướng trung bình"
    )

    plt.title(
        f"[{country}] Hệ số gom cụm theo Bậc (Clustering vs Degree)"
    )

    plt.xlabel("Bậc của Node (Degree)")
    plt.ylabel("Hệ số gom cụm (Clustering Coefficient)")
    plt.xscale("log")
    plt.legend()

    out_path = Path(output_dir) / "clustering_vs_degree.png"

    plt.savefig(
        out_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return out_path

def plot_model_comparison(comparison_csv_path: Path, output_dir: Path):
    """Vẽ biểu đồ cột so sánh các chỉ số giữa Mạng thực tế và 3 mô hình giả lập"""
    set_seaborn_style()
    
    if not comparison_csv_path.exists():
        print(f"Không tìm thấy file {comparison_csv_path} để vẽ so sánh mô hình.")
        return
        
    df = pd.read_csv(comparison_csv_path)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Đồ thị 1: So sánh Clustering Coefficient
    sns.barplot(data=df, x="country", y="average_clustering", hue="model", ax=axes[0], palette="muted")
    axes[0].set_title("So sánh Hệ số gom cụm (Clustering)")
    axes[0].set_ylabel("Average Clustering Coefficient")
    axes[0].set_xlabel("Quốc gia")
    
    # Đồ thị 2: So sánh Average Shortest Path Length
    sns.barplot(data=df, x="country", y="average_shortest_path_length", hue="model", ax=axes[1], palette="muted")
    axes[1].set_title("So sánh Đường đi trung bình (Shortest Path)")
    axes[1].set_ylabel("Average Shortest Path Length")
    axes[1].set_xlabel("Quốc gia")
    
    plt.suptitle("So sánh Mạng thực tế YouTube với các Mô hình ngẫu nhiên", fontsize=18, y=1.02)
    
    out_path = Path(output_dir) / "model_comparison.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    return out_path

def generate_interactive_network(G: nx.Graph, country: str, output_dir: Path, max_nodes: int = 300):
    """
    Trực quan hóa mạng lưới tương tác bằng PyVis dạng HTML.
    Vì đồ thị gốc >2000 nodes rất nặng, hàm này sẽ lấy top các node có bậc cao nhất (Hubs) 
    để tạo đồ thị HTML mượt mà, dễ tương tác trên trình duyệt.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "interactive_graph.html"
    top_nodes = [node for node, degree in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]]
    subG = G.subgraph(top_nodes).copy()
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", select_menu=True)  # type: ignore    
    # Tính toán kích thước node dựa trên PageRank để thể hiện quyền lực của kênh
    pagerank = nx.pagerank(subG)
    
    for node in subG.nodes():
        size = pagerank[node] * 1000 + 10  # Chuẩn hóa kích thước node
        degree = G.degree(node)
        # Thêm thông tin khi di chuột vào node (Tooltip)
        title = f"Kênh: {node}<br>Số cạnh kết nối (Total Degree): {degree}"
        net.add_node(
        str(node),
        label=str(node),
        size=size,
        title=title
    )
        
    for u, v, data in subG.edges(data=True):
        weight = data.get('weight', 1)
        net.add_edge(
        str(u),
        str(v),
        value=weight,
        title=f"Số lần co-trending: {weight}",
        color="#888888"
    )
            
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150, spring_strength=0.05, damping=0.95)
    
    html = net.generate_html()
    with open(
        out_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    return out_path 
    