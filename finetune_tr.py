import os
# TF/Flax modüllerini devre dışı bırak (yalnızca PyTorch kullan)
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")

import pandas as pd
import numpy as np
import torch
from datasets import Dataset, DatasetDict
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          DataCollatorWithPadding, TrainingArguments, Trainer)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data_tr')
TRAIN_CSV = os.path.join(DATA_DIR, 'train.csv')
VAL_CSV = os.path.join(DATA_DIR, 'val.csv')
MODEL_NAME = 'savasy/bert-base-turkish-sentiment-cased'
OUTPUT_DIR = os.path.join(BASE_DIR, 'models_tr', 'bert_tr_finetuned')
LABEL2ID = {'negatif': 0, 'nötr': 1, 'pozitif': 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}


def load_datasets():
    train_df = pd.read_csv(TRAIN_CSV)
    val_df = pd.read_csv(VAL_CSV)

    # text/label sütunlarını garanti altına al
    assert 'text' in train_df.columns and 'label' in train_df.columns

    train_ds = Dataset.from_pandas(train_df[['text', 'label']])
    val_ds = Dataset.from_pandas(val_df[['text', 'label']])
    return DatasetDict({'train': train_ds, 'validation': val_ds})


def tokenize_function(examples, tokenizer):
    return tokenizer(examples['text'], truncation=True, max_length=256)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {'accuracy': acc, 'f1': f1, 'precision': p, 'recall': r}


# Eski Transformers sürümleri için compute_loss'u override eden Trainer
class CustomTrainer(Trainer):
    def __init__(self, class_weights: torch.Tensor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        if self.class_weights is not None and self.args.device.type == 'cuda':
            self.class_weights = self.class_weights.to(self.args.device)

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get('labels')
        outputs = model(**{k: v for k, v in inputs.items() if k != 'labels'})
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    datasets = load_datasets()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    tokenized = datasets.map(lambda x: tokenize_function(x, tokenizer), batched=True, remove_columns=['text'])

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        ignore_mismatched_sizes=True
    )

    # Eski Transformers sürümleriyle uyumlu minimal argümanlar
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        weight_decay=0.01,
        fp16=torch.cuda.is_available(),
        logging_steps=50
    )

    # Sınıf ağırlıkları (inverse frequency)
    train_counts = pd.read_csv(TRAIN_CSV)['label'].value_counts().to_dict()
    total = sum(train_counts.values())
    class_weights = torch.tensor([
        total / (3 * train_counts.get(LABEL2ID['negatif'], 1)),
        total / (3 * train_counts.get(LABEL2ID['nötr'], 1)),
        total / (3 * train_counts.get(LABEL2ID['pozitif'], 1)),
    ], dtype=torch.float32)

    trainer = CustomTrainer(
        class_weights=class_weights,
        model=model,
        args=args,
        train_dataset=tokenized['train'],
        eval_dataset=tokenized['validation'],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    print('Eğitim tamamlandı. Model kaydedildi ->', OUTPUT_DIR)


if __name__ == '__main__':
    main()
