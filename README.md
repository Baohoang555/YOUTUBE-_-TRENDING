# YouTube Trending Network Analysis

> Phân tích mạng xã hội YouTube Trending (US) sử dụng các mô hình Random Graph, Small-world và Preferential Attachment — kèm so sánh đa quốc gia (US vs GB).

---

## Thành viên nhóm

| Thành viên | Vai trò | Nhiệm vụ chính |
|---|---|---|
| Bao | Model Comparison & Integration | ER / BA / WS models, cross-country comparison, merge kết quả |
| Tho | Data & Graph Construction | Load data, làm sạch, xây graph, export |
| Huy | Network Analysis | Degree distribution, power-law, centrality, community |
| Trung | Visualization & Report | Figures, PyVis, report, slide |

---

## Mô tả đề tài

Đề tài phân tích cấu trúc mạng lưới các YouTube channel trending tại Mỹ (US) thông qua các mô hình lý thuyết đồ thị kinh điển:

- **Erdős–Rényi (ER)** — Random Graph Model
- **Barabási–Albert (BA)** — Preferential Attachment
- **Watts–Strogatz (WS)** — Small-world Network

Sau khi phân tích mạng US, nhóm áp dụng cùng phương pháp lên dataset GB để đánh giá tính tổng quát của mô hình (*cross-country comparison*).

---

## Dataset

| File | Nguồn | Mô tả |
|---|---|---|
| `USvideos.csv` | Kaggle | ~40,000 trending videos tại Mỹ |
| `GBvideos.csv` | Kaggle | ~38,000 trending videos tại Anh |
| `US_category_id.json` | Kaggle | Mapping category_id → tên |
| `GB_category_id.json` | Kaggle | Mapping category_id → tên |

**Link download:** https://www.kaggle.com/datasets/datasnaek/youtube-new

> Sau khi tải về, đặt tất cả file vào thư mục `data/`

---

## Cấu trúc thư mục

```
youtube-network/
│
├── data/                          ← Đặt CSV + JSON vào đây
│   ├── USvideos.csv
│   ├── GBvideos.csv
│   ├── US_category_id.json
│   └── GB_category_id.json
│
├── notebooks/                     ← Jupyter notebooks theo từng bước
│   ├── 01_data_graph.ipynb        ← Member 2: Load, clean, build graph
│   ├── 02_analysis.ipynb          ← Member 3: Metrics, power-law, community
│   └── 03_models.ipynb            ← Leader: ER/BA/WS + US vs GB comparison
│
├── src/                           ← Module Python tái sử dụng
│   ├── loader.py                  ← Load & làm sạch dữ liệu
│   ├── graph_builder.py           ← Xây weighted graph
│   ├── metrics.py                 ← Tính network metrics + power-law
│   ├── models.py                  ← Sinh ER / BA / WS + so sánh
│   └── visualization.py           ← Tất cả plots + interactive graph
│
├── output/                        ← Toàn bộ kết quả export vào đây
│   ├── figures/                   ← PNG plots (dùng trong report/slide)
│   │   ├── degree_distribution.png
│   │   ├── clustering_vs_degree.png
│   │   ├── model_comparison.png
│   │   └── communities.png
│   ├── graphs/                    ← Interactive HTML graph
│   │   └── interactive_graph.html
│   └── tables/                    ← CSV + JSON kết quả số liệu
│       ├── basic_metrics.json
│       ├── centrality.csv
│       ├── model_comparison.csv
│       └── powerlaw.json
│
├── report/                        ← Báo cáo cuối kỳ
│   ├── report.docx
│   └── slides.pptx
│
├── main.py                        ← Chạy toàn bộ pipeline 1 lệnh
├── requirements.txt               ← Danh sách thư viện
└── README.md
```

---

## Cài đặt

### Yêu cầu

- Python 3.9+
- pip

### Cài thư viện

```bash
pip install -r requirements.txt
```

---

## Cách chạy

### Chạy toàn bộ pipeline (khuyên dùng)

```bash
python main.py
```

Pipeline sẽ tự động chạy theo thứ tự:

```
[1] Load & clean USvideos.csv + US_category_id.json
[2] Build weighted graph (node = channel, edge = co-trending)
[3] Compute network metrics (clustering, diameter, path length, ...)
[4] Compute centrality (degree, betweenness, PageRank)
[5] Fit power-law + KS-test
[6] Generate ER / BA / WS synthetic graphs
[7] Compare real vs synthetic
[8] Plot all figures → output/figures/
[9] Export interactive graph → output/graphs/interactive_graph.html
[10] Export metrics tables → output/tables/
```

### Chạy từng notebook riêng lẻ

```bash
jupyter notebook notebooks/01_data_graph.ipynb
jupyter notebook notebooks/02_analysis.ipynb
jupyter notebook notebooks/03_models.ipynb
```

---

## Phương pháp

### 1. Xây dựng graph

- **Node** = YouTube channel
- **Edge** = hai channel cùng trending trong cùng `category_id` và cùng `trending_date`
- **Weight** = số lần co-trending

### 2. Network metrics tính toán

| Metric | Ý nghĩa |
|---|---|
| Degree distribution | Phân phối bậc của node |
| Power-law exponent (α) | Kiểm định rich-get-richer |
| Clustering coefficient | Mức độ "bạn của bạn cũng là bạn" |
| Average shortest path | Kiểm chứng small-world |
| Graph diameter | Đường kính mạng |
| Betweenness centrality | Channel đóng vai trò cầu nối |
| PageRank | Ảnh hưởng thực sự trong mạng |
| Modularity (Louvain) | Chất lượng phân cụm cộng đồng |

### 3. So sánh mô hình

So sánh graph thực tế với 3 mô hình sinh:

| Mô hình | Đặc trưng |
|---|---|
| Erdős–Rényi (ER) | Random, không có hub |
| Barabási–Albert (BA) | Preferential attachment, có hub, power-law |
| Watts–Strogatz (WS) | Small-world, clustering cao |

### 4. So sánh đa quốc gia (US vs GB)

Áp dụng cùng phương pháp phân tích lên GBvideos.csv và so sánh các chỉ số mạng giữa hai quốc gia để đánh giá tính tổng quát của mô hình.

---

## Kết quả đầu ra

| File | Mô tả |
|---|---|
| `output/figures/degree_distribution.png` | Log-log plot + power-law fit |
| `output/figures/clustering_vs_degree.png` | Clustering coefficient vs degree |
| `output/figures/model_comparison.png` | Real vs ER / BA / WS |
| `output/figures/communities.png` | Community structure (Louvain) |
| `output/graphs/interactive_graph.html` | Mở bằng browser để demo |
| `output/tables/basic_metrics.json` | Toàn bộ network metrics |
| `output/tables/centrality.csv` | Degree / betweenness / PageRank |
| `output/tables/model_comparison.csv` | Bảng so sánh các mô hình |
| `output/tables/powerlaw.json` | Kết quả kiểm định power-law |

---

## Công nghệ sử dụng

| Công cụ | Mục đích |
|---|---|
| `NetworkX` | Xây dựng và phân tích graph |
| `powerlaw` | Fitting và kiểm định power-law (KS-test) |
| `python-louvain` | Community detection (Louvain algorithm) |
| `PyVis` | Interactive graph visualization |
| `Matplotlib / Seaborn` | Static plots |
| `Pandas` | Xử lý dữ liệu |

---

## Câu hỏi giảng viên thường hỏi

**Q: Tại sao chọn co-trending làm định nghĩa edge?**  
A: Hai channel trending cùng ngày, cùng category phản ánh sự cạnh tranh/tương đồng về nội dung — đây là quan hệ mạng xã hội có ý nghĩa thực tế trong hệ sinh thái YouTube.

**Q: Mô hình nào fit thực tế nhất?**  
A: BA model (Barabási–Albert) — vì degree distribution của mạng thực tế tuân theo power-law (α ≈ 2–3), phù hợp với cơ chế preferential attachment: channel lớn ngày càng trending nhiều hơn.

**Q: Small-world có xuất hiện không?**  
A: Có thể kiểm chứng qua chỉ số sigma = (C/C_rand) / (L/L_rand). Nếu sigma > 1 thì xác nhận small-world.

**Q: Tại sao so sánh US vs GB?**  
A: Để kiểm tra tính tổng quát (generalizability) của mô hình — nếu BA model fit tốt cả US lẫn GB thì kết luận về preferential attachment có giá trị học thuật cao hơn.

---

## Tài liệu tham khảo

1. Barabási, A.-L., & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509–512.
2. Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. *Nature*, 393, 440–442.
3. Erdős, P., & Rényi, A. (1960). On the evolution of random graphs. *Publications of the Mathematical Institute of the Hungarian Academy of Sciences*.
4. Kaggle Dataset: [Trending YouTube Video Statistics](https://www.kaggle.com/datasets/datasnaek/youtube-new)
