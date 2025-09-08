import os
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_CSV = os.path.join(BASE_DIR, 'Mardin_temiz.csv')
OUT_DIR = os.path.join(BASE_DIR, 'data_tr')
TRAIN_CSV = os.path.join(OUT_DIR, 'train.csv')
VAL_CSV = os.path.join(OUT_DIR, 'val.csv')

LABEL2ID = {'negatif': 0, 'nötr': 1, 'pozitif': 2}


def title_to_sentiment(title: str) -> str:
    t = str(title).lower()
    pos = [
        'efsaneydi','mükemmel','harika','süper','lezzetli','güzel',
        'muhteşem','tavsiye','öneririm','beğendim','memnun','iyi',
        'hoş','keyifli','başarılı','kaliteli','temiz','harikulade','efsane'
    ]
    neg = [
        'kötü','berbat','rezalet','vasat','hayal kırıklığı','pahalı',
        'soğuk','yanmış','bayat','bekledik','geç','kirli','rezil','fiyasko',
        'pişman','pişmanlık','asla','tavsiye etmiyorum','tavsiye etmem'
    ]
    if any(k in t for k in pos):
        return 'pozitif'
    if any(k in t for k in neg) or ('en kötü' in t or 'en kotu' in t):
        return 'negatif'
    return 'nötr'


def balance_dataframe(df: pd.DataFrame, target_col: str, max_per_class: int = 2000) -> pd.DataFrame:
    parts = []
    for label, group in df.groupby(target_col):
        if len(group) > max_per_class:
            parts.append(group.sample(n=max_per_class, random_state=42))
        else:
            # upsample with replacement to the size of the largest or keep as-is
            parts.append(group)
    df_bal = pd.concat(parts, axis=0).sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df_bal


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(SRC_CSV)
    # metni oluştur
    df['text'] = (df['review_title'].fillna('') + ' ' + df['clean_review'].fillna('')).str.strip()
    df = df[df['text'].str.len() > 0].copy()

    # zayıf etiket
    df['label_str'] = df['review_title'].apply(title_to_sentiment)
    df['label'] = df['label_str'].map(LABEL2ID)

    # temel filtre: aşırı kısa metinleri at
    df = df[df['text'].str.len() >= 10].copy()

    # sınıfları gözlemle
    print(df['label_str'].value_counts())

    # dengeli split
    train_df, val_df = train_test_split(
        df[['text','label','label_str']],
        test_size=0.2,
        random_state=42,
        stratify=df['label']
    )

    # sınıf dengesini biraz düzelt (aşırı olanları downsample et)
    train_df = balance_dataframe(train_df, 'label_str', max_per_class=2000)

    # kaydet
    train_df.to_csv(TRAIN_CSV, index=False)
    val_df.to_csv(VAL_CSV, index=False)
    print('Kaydedildi ->', TRAIN_CSV)
    print('Kaydedildi ->', VAL_CSV)


if __name__ == '__main__':
    main()
