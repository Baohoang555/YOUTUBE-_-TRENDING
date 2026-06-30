import json
from pathlib import Path
 
import pandas as pd
 
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
 
 
def load_category_map(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        category_data = json.load(f)
 
    return {
        int(item["id"]): item["snippet"]["title"]
        for item in category_data["items"]
    }
 
 
def load_raw_data(country: str, data_dir: Path = DEFAULT_DATA_DIR) -> pd.DataFrame:
    data_dir = Path(data_dir)
    csv_path = data_dir / f"{country}videos.csv"
 
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {csv_path}. "
            f"Hãy tải dataset từ Kaggle và đặt vào thư mục data/."
        )
 
    df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
    return df
 
 
def clean_data(df: pd.DataFrame, category_map: dict) -> pd.DataFrame:
    """
    Làm sạch dữ liệu:
    - Loại video lỗi / đã bị xóa (video_error_or_removed = True)
    - Loại dòng thiếu channel_title / category_id / trending_date
    - Map category_id -> category_name
    - Chuẩn hóa trending_date (format gốc: YY.DD.MM)
    - Loại video trùng trong cùng 1 ngày (đề phòng crawl lặp)
    """
    df = df.copy()
 
    if "video_error_or_removed" in df.columns:
        df = df[df["video_error_or_removed"] == False]
 
    df = df.dropna(subset=["channel_title", "category_id", "trending_date"])
 
    df["category_id"] = df["category_id"].astype(int)
    df["category_name"] = df["category_id"].map(category_map)
    df = df.dropna(subset=["category_name"])
 
    df["trending_date"] = pd.to_datetime(
        df["trending_date"], format="%y.%d.%m", errors="coerce"
    )
    df = df.dropna(subset=["trending_date"])
 
    df = df.drop_duplicates(subset=["video_id", "trending_date"])
 
    return df.reset_index(drop=True)
 
 
def load_and_clean(country: str, data_dir: Path = DEFAULT_DATA_DIR) -> pd.DataFrame:
    """
    Hàm tiện ích gọi 1 lần: load raw data + category map + clean.
    country: "US" hoặc "GB"
    """
    data_dir = Path(data_dir)
    df_raw = load_raw_data(country, data_dir)
    category_map = load_category_map(data_dir / f"{country}_category_id.json")
    df_clean = clean_data(df_raw, category_map)
    return df_clean
 
 
def save_cleaned(df: pd.DataFrame, country: str, output_dir: Path) -> Path:
    """
    Lưu dữ liệu đã làm sạch ra output/tables/{country}_cleaned.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{country}_cleaned.csv"
    df.to_csv(out_path, index=False)
    return out_path
 
 
if __name__ == "__main__":
    for country in ["US", "GB"]:
        try:
            df = load_and_clean(country)
            print(
                f"[{country}] Số dòng sau làm sạch: {len(df):,} | "
                f"Số channel: {df['channel_title'].nunique():,}"
            )
        except FileNotFoundError as e:
            print(f"[{country}] {e}")
 