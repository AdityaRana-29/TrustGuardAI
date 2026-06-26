"""
BERT-based Scam Detector (Advanced)
Uses HuggingFace transformers for higher accuracy.

Requirements: torch, transformers, datasets
Run: python ml/bert_scam_detector.py

NOTE: Requires GPU or will be slow on CPU.
"""
import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "bert_scam")
os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5
MODEL_NAME = "bert-base-uncased"


# ---- Dataset ----
TEXTS = [
    # Scam (1)
    "Congratulations you won Rs 25 lakh click here to claim prize immediately",
    "Your KYC is pending update now or your bank account will be blocked",
    "Earn Rs 5000 per day from home no experience required WhatsApp now",
    "Send your OTP to reverse the fraudulent transaction on your account",
    "You have been selected for lucky draw winner claim your reward now",
    "Investment opportunity double your money in 30 days guaranteed returns crypto",
    "Dear customer SBI account suspended verify immediately http://sbi-xyz.tk",
    "Work from home data entry job earn 800 per hour no qualification needed",
    "Court notice pending EMI bounce case pay immediately to avoid arrest",
    "Free Jio recharge 3 months limited offer forward to 10 friends claim now",
    "Your UPI account hacked reverse transaction send OTP to helpdesk",
    "Lottery winner congratulations transfer processing fee to release prize",
    "Click here to update your Aadhaar or lose access to government benefits",
    "You have won iPhone 15 in Facebook lucky draw claim before expires",
    "Immediate action required your credit card blocked verify now",
    # Safe (0)
    "Hi can we reschedule the meeting to 3 PM tomorrow",
    "Your order has been shipped expected delivery 2 to 3 days",
    "Please find attached the Q3 financial report for review",
    "Reminder team lunch at 1 PM today in the cafeteria",
    "Your OTP for net banking login is 847291 valid for 10 minutes do not share",
    "The weather today is expected to be sunny with light clouds",
    "Happy birthday! Wishing you all the best on your special day",
    "The project deadline has been extended by one week",
    "Please confirm your attendance for the conference next Monday",
    "Your flight to Mumbai departs at 6 AM gate 14",
    "New book recommendation: Atomic Habits by James Clear",
    "The board meeting is scheduled for Friday at 11 AM",
    "Please submit your timesheets by end of day Friday",
    "Library books are due for return by end of month",
    "Gym schedule has been updated check the noticeboard",
]

LABELS = [1] * 15 + [0] * 15  # 1=scam, 0=safe


class ScamDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def train():
    print(f"Loading tokenizer: {MODEL_NAME}")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

    X_train, X_test, y_train, y_test = train_test_split(
        TEXTS, LABELS, test_size=0.2, random_state=42, stratify=LABELS
    )

    train_dataset = ScamDataset(X_train, y_train, tokenizer, MAX_LEN)
    test_dataset = ScamDataset(X_test, y_test, tokenizer, MAX_LEN)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, eps=1e-8)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    print(f"\nTraining BERT for {EPOCHS} epochs...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.4f}")

    # Evaluate
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            outputs = model(input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(batch["labels"].numpy())

    acc = accuracy_score(all_labels, all_preds)
    print(f"\nTest Accuracy: {acc:.4f}")
    print(classification_report(all_labels, all_preds, target_names=["Safe", "Scam"]))

    # Save model
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"\n✅ BERT model saved to {MODEL_DIR}")


def predict(text: str) -> dict:
    """Run inference with saved BERT model."""
    tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
    model.eval()
    model.to(DEVICE)

    encoding = tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(
            encoding["input_ids"].to(DEVICE),
            attention_mask=encoding["attention_mask"].to(DEVICE),
        )

    probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
    pred = int(np.argmax(probs))

    return {
        "label": "Scam" if pred == 1 else "Safe",
        "scam_probability": round(probs[1] * 100, 1),
        "safe_probability": round(probs[0] * 100, 1),
    }


if __name__ == "__main__":
    train()
    # Quick test after training
    test_texts = [
        "Congratulations! You won Rs 10 lakh. Click here to claim.",
        "Hi, let's meet at 3 PM for the project review.",
    ]
    for t in test_texts:
        result = predict(t)
        print(f"[{result['label']} — Scam: {result['scam_probability']}%] {t}")
