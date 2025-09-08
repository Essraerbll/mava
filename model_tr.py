# model_tr.py
import os
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Gürültü/uyarı azaltma
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

# Script dizini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ====== Ayarlar ======
MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"  # Türkçe için uygun model (cased)
CSV_IN     = os.path.join(BASE_DIR, "Mardin_temiz.csv")   # Temizlenmiş veri mutlak yol
CSV_OUT    = os.path.join(BASE_DIR, "restaurant_sentiment_bert_tr.csv")  # Çıktı mutlak yol
TEXT_COLS  = ("review_title", "clean_review")     # metin için birleştirilecek kolonlar
GROUP_COL  = "restaurant_name"                     # restoran ismi kolonu
MINI_BATCH_CPU = 32
MINI_BATCH_GPU = 128
# =====================

def load_dataframe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV bulunamadı: {path}")
    for enc in (None, "utf-8", "utf-8-sig", "cp1254"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    return pd.read_csv(path, engine="python")

def build_text_column(df: pd.DataFrame, title_col: str, text_col: str) -> pd.Series:
    if title_col not in df.columns or text_col not in df.columns:
        missing = [c for c in (title_col, text_col) if c not in df.columns]
        raise KeyError(f"Eksik kolon(lar): {missing}. CSV’de bu kolonlar olmalı: {title_col}, {text_col}")
    return (df[title_col].fillna("") + " " + df[text_col].fillna("")).str.strip()

def label_to_category(label: str) -> str:
    # savasy/bert-base-turkish-sentiment: labels genelde Negative/Neutral/Positive
    lab = str(label).lower()
    if "neg" in lab:
        return "negatif"
    if "neu" in lab:
        return "nötr"
    return "pozitif"

def main():
    # 1) Cihaz
    use_gpu = torch.cuda.is_available()
    device  = 0 if use_gpu else -1
    print(f"GPU aktif mi? {use_gpu} | device={device}")

    # 2) Model + Tokenizer
    print("Model yükleniyor (TR)...")
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if use_gpu else torch.float32
    )
    if use_gpu:
        model = model.to("cuda")
        torch.backends.cuda.matmul.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass

    clf = pipeline(
        task="sentiment-analysis",
        model=model,
        tokenizer=tok,
        device=device,
        truncation=True
    )

    # 3) Veriyi yükle
    print("CSV dosyası okunuyor...")
    df = load_dataframe(CSV_IN)
    if GROUP_COL not in df.columns:
        raise KeyError(f"Eksik kolon: {GROUP_COL}")

    df["text"] = build_text_column(df, TEXT_COLS[0], TEXT_COLS[1])

    # Boş metinleri temizle
    df = df[df["text"].astype(str).str.len() > 0].copy()
    if df.empty:
        raise ValueError("Analiz edilecek metin bulunamadı (tüm metinler boş).")

    # 4) Batch tahmin
    print("Türkçe sentiment analizi yapılıyor...")
    BATCH = MINI_BATCH_GPU if use_gpu else MINI_BATCH_CPU
    preds, scores = [], []

    with torch.inference_mode():
        # pipeline kendi batching’ini yapar; yine de dilimleyelim
        for i in range(0, len(df), BATCH):
            batch = df["text"].iloc[i:i+BATCH].tolist()
            out = clf(batch)
            preds.extend([label_to_category(o["label"]) for o in out])
            scores.extend([o["score"] for o in out])

    # 5) Sonuçlar
    print("Sonuçlar işleniyor...")
    df["sentiment_category"] = preds
    df["sentiment_score"] = scores

    # 6) Restoran bazında özet
    agg = (
        df.groupby(GROUP_COL)["sentiment_category"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )
    for c in ("pozitif", "negatif", "nötr"):
        if c not in agg.columns:
            agg[c] = 0

    agg["toplam"] = agg[["pozitif", "negatif", "nötr"]].sum(1)
    agg["pozitif_%"] = (agg["pozitif"] / agg["toplam"] * 100).round(1)
    agg["negatif_%"] = (agg["negatif"] / agg["toplam"] * 100).round(1)

    agg.sort_values(["pozitif_%", "toplam"], ascending=[False, False]).to_csv(CSV_OUT, index=False)

    print("Bitti ->", CSV_OUT)
    print(f"Toplam {len(df)} yorum analiz edildi")

if __name__ == "__main__":
    try:
        main()
    except torch.cuda.OutOfMemoryError:
        print("CUDA OOM: BATCH’i küçült (ör. 64/32) ve tekrar dene.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        print("CSV ve kolonları kontrol et (örn. restaurant_name, review_title, clean_review).")
