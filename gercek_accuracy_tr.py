import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_IN = os.path.join(BASE_DIR, "Mardin_temiz.csv")
MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"


def load_and_label_data():
    print("Veri yükleniyor:", CSV_IN)
    df = pd.read_csv(CSV_IN)

    def title_to_sentiment(title: str) -> str:
        t = str(title).lower()
        pos = [
            'efsaneydi','mükemmel','harika','süper','lezzetli','güzel',
            'muhteşem','tavsiye','öneririm','beğendim','memnun','iyi',
            'hoş','keyifli','başarılı','kaliteli','temiz'
        ]
        neg = [
            'kötü','berbat','rezalet','vasat','hayal kırıklığı','pahalı',
            'soğuk','yanmış','bayat','bekledik','geç','kirli'
        ]
        if any(k in t for k in pos):
            return 'pozitif'
        if any(k in t for k in neg) or ('en kötü' in t or 'en kotu' in t):
            return 'negatif'
        return 'nötr'

    df['gercek_sentiment'] = df['review_title'].apply(title_to_sentiment)
    return df


def run_tr_model(df: pd.DataFrame, sample_size: int = 500) -> pd.DataFrame:
    print(f"TR model ile {min(sample_size, len(df))} yorum değerlendiriliyor...")
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42).copy()

    use_gpu = torch.cuda.is_available()
    device = 0 if use_gpu else -1
    print(f"GPU aktif mi? {use_gpu}")

    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if use_gpu else torch.float32
    )
    if use_gpu:
        model = model.to('cuda')

    clf = pipeline(
        task='sentiment-analysis',
        model=model,
        tokenizer=tok,
        device=device,
        truncation=True
    )

    sample_df['text'] = (sample_df['review_title'].fillna('') + ' ' +
                         sample_df['clean_review'].fillna('')).str.strip()
    sample_df = sample_df[sample_df['text'].str.len() > 0].copy()

    preds = []
    for txt in sample_df['text']:
        try:
            r = clf(txt)[0]['label'].lower()
            if 'neg' in r:
                preds.append('negatif')
            elif 'neu' in r:
                preds.append('nötr')
            else:
                preds.append('pozitif')
        except Exception:
            preds.append('nötr')

    sample_df['pred_sentiment'] = preds
    return sample_df


def evaluate(df: pd.DataFrame):
    y_true = df['gercek_sentiment']
    y_pred = df['pred_sentiment']

    acc = accuracy_score(y_true, y_pred)
    print(f"Accuracy: {acc:.3f} ({acc*100:.1f}%)")

    print("\nClassification report:\n", classification_report(y_true, y_pred))

    cm = confusion_matrix(y_true, y_pred, labels=['pozitif','nötr','negatif'])
    print("Confusion Matrix (rows=true, cols=pred):")
    print(cm)

    out_csv = os.path.join(BASE_DIR, 'accuracy_test_tr_results.csv')
    df.to_csv(out_csv, index=False)
    print("Kaydedildi ->", out_csv)


def main():
    df = load_and_label_data()
    df_eval = run_tr_model(df, sample_size=500)
    evaluate(df_eval)


if __name__ == '__main__':
    main()
