"""
Train Scam / Spam Detection Model
Dataset: SMS Spam Collection (UCI)
Models: Logistic Regression, Random Forest, (optionally BERT)

Run: python ml/train_scam_model.py
"""
import os
import urllib.request
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

DATASET_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "sms_spam.tsv")


def download_dataset():
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    if not os.path.exists(DATASET_PATH):
        print(f"Downloading SMS Spam dataset...")
        urllib.request.urlretrieve(DATASET_URL, DATASET_PATH)
        print(f"Dataset saved to {DATASET_PATH}")
    else:
        print(f"Dataset already exists at {DATASET_PATH}")


def load_data():
    df = pd.read_csv(DATASET_PATH, sep="\t", header=None, names=["label", "text"])
    print(f"Dataset shape: {df.shape}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    df["binary_label"] = (df["label"] == "spam").astype(int)
    return df


def augment_with_scam_examples(df: pd.DataFrame) -> pd.DataFrame:
    """Add custom Indian scam examples to improve model relevance."""
    custom_data = [
        # Scam examples
        ("spam", "Congratulations! You have won Rs 25 lakh in lucky draw. Call 9876543210 to claim."),
        ("spam", "Your KYC is pending. Update immediately or your account will be blocked. Click here."),
        ("spam", "Earn Rs 5000 daily from home. No experience needed. WhatsApp us now!"),
        ("spam", "UPI fraud alert: Your account will be debited. Share OTP to reverse transaction."),
        ("spam", "IRCTC Lucky winner! You won free train tickets. Verify Aadhaar to claim."),
        ("spam", "Investment opportunity: Double your money in 30 days with crypto. 100% guaranteed returns."),
        ("spam", "Dear customer, your SBI account is suspended. Verify now: http://sbi-update.xyz"),
        ("spam", "You have been selected for part time job. Earn 800 per hour. Send resume on WhatsApp."),
        ("spam", "Court notice: You have pending EMI bounce case. Pay now to avoid arrest."),
        ("spam", "Free Jio recharge 3 months. Limited offer. Forward to 10 friends and claim."),
        # Ham examples
        ("ham", "Hi, can we reschedule the meeting to 3 PM tomorrow?"),
        ("ham", "Your order has been shipped. Expected delivery: 2-3 days."),
        ("ham", "Please find attached the report for Q3 review."),
        ("ham", "Reminder: Team lunch at 1 PM today in the cafeteria."),
        ("ham", "Your OTP for login is 847291. Valid for 10 minutes. Do not share."),
    ]
    extra = pd.DataFrame(custom_data, columns=["label", "text"])
    extra["binary_label"] = (extra["label"] == "spam").astype(int)
    return pd.concat([df, extra], ignore_index=True)


def train_logistic_regression(X_train, X_test, y_train, y_test):
    print("\n--- Training Logistic Regression ---")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=50000,
            min_df=2,
            strip_accents="unicode",
            analyzer="word",
        )),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))
    return pipeline, acc


def train_random_forest(X_train, X_test, y_train, y_test):
    print("\n--- Training Random Forest ---")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=20000,
            min_df=2,
            strip_accents="unicode",
        )),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            class_weight="balanced",
            n_jobs=-1,
            random_state=42,
        )),
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))
    return pipeline, acc


def save_best_model(models: list):
    best_pipeline, best_acc, best_name = max(models, key=lambda x: x[1])
    print(f"\n✅ Best model: {best_name} ({best_acc:.4f})")
    path = os.path.join(MODEL_DIR, "scam_model.joblib")
    joblib.dump(best_pipeline, path)
    print(f"Model saved to {path}")


def main():
    download_dataset()
    df = load_data()
    df = augment_with_scam_examples(df)

    X = df["text"].values
    y = df["binary_label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTraining size: {len(X_train)}, Test size: {len(X_test)}")

    lr_model, lr_acc = train_logistic_regression(X_train, X_test, y_train, y_test)
    rf_model, rf_acc = train_random_forest(X_train, X_test, y_train, y_test)

    save_best_model([
        (lr_model, lr_acc, "Logistic Regression"),
        (rf_model, rf_acc, "Random Forest"),
    ])

    # Test with sample predictions
    print("\n--- Sample Predictions ---")
    best_model = joblib.load(os.path.join(MODEL_DIR, "scam_model.joblib"))
    samples = [
        "Congratulations! You won Rs 10 lakh. Click here to claim.",
        "Hi Rahul, meeting tomorrow at 10 AM. Please bring the report.",
        "Your KYC is pending. Update now or account blocked.",
        "Mom, can you please call me when you're free?",
    ]
    preds = best_model.predict(samples)
    probs = best_model.predict_proba(samples)
    for text, pred, prob in zip(samples, preds, probs):
        label = "SPAM/SCAM" if pred == 1 else "HAM/SAFE"
        confidence = max(prob) * 100
        print(f"[{label} {confidence:.1f}%] {text[:60]}...")


if __name__ == "__main__":
    main()
