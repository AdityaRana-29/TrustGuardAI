"""
Train Fake News Detection Model
Dataset: Fake and Real News Dataset (Kaggle)
Models: TF-IDF + Naive Bayes, Logistic Regression

Run: python ml/train_fake_news_model.py
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def build_demo_dataset() -> pd.DataFrame:
    """
    Build a demo dataset for training.
    In production, replace with Fake and Real News Dataset (Kaggle):
    https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset
    """
    print("Building demo dataset (replace with full Kaggle dataset for better accuracy)...")

    fake_samples = [
        "SHOCKING: Scientists discover miracle cure that big pharma is hiding!",
        "Government cover-up exposed — they don't want you to know the hidden truth!",
        "Deep state conspiracy revealed! Share before it gets deleted!",
        "Doctors HATE this one weird trick that cures diabetes instantly!",
        "BREAKING: PM arrested for secret corruption — mainstream media won't cover this!",
        "Anonymous source reveals election was rigged. Stolen ballot boxes found!",
        "Mind-blowing footage suppressed by government. Watch before banned!",
        "Bombshell revelation: secret agenda of world leaders exposed by insider!",
        "You won't believe what they found hidden in the moon! NASA cover-up!",
        "Wake up! The fluoride in water is making you sick — share now!",
        "Vaccine causes autism confirmed by suppressed study — doctors hiding truth!",
        "Illuminati controls world economy — shocking proof leaked!",
        "100% proven: This banned herb reverses cancer in days!",
        "Breaking: Famous politician dead — media blackout in effect!",
        "They are replacing real food with lab-grown poison — expose the truth!",
        "Secret UN plan to reduce world population confirmed by whistleblower!",
        "Share before deleted: Government admits chemtrails are real!",
        "Explosive: Deep state planning false flag attack this month!",
        "Unbelievable: Moon landing was faked, new evidence proves it!",
        "Jaw-dropping: Alien bases found on Mars, NASA lying for decades!",
    ]

    real_samples = [
        "The government announced new infrastructure spending of Rs 500 crore for road development.",
        "According to official data, GDP growth slowed to 6.5% in the last quarter.",
        "The Supreme Court issued a verdict today on the land acquisition case.",
        "Scientists published new research in Nature journal about climate patterns.",
        "The RBI governor confirmed that inflation remains within target range.",
        "Press release: Health ministry launches new vaccination drive in rural areas.",
        "Confirmed by officials: New metro line will be inaugurated next month.",
        "The election commission announced polling dates for upcoming state elections.",
        "Ministry of Finance released annual budget highlights today.",
        "The police confirmed the arrest of three suspects in the robbery case.",
        "Weather department predicts normal monsoon this year, official statement.",
        "University releases admission schedule for 2025-26 academic year.",
        "ISRO successfully launched communication satellite into geostationary orbit.",
        "Government sources confirm new education policy implementation timeline.",
        "Stock market closed higher today on positive global cues.",
        "New study by IIT researchers finds cost-effective water purification method.",
        "State government signs MoU with private firm for renewable energy project.",
        "Traffic police issued advisory for road closure during repair work this weekend.",
        "Hospital opens new trauma center with state-of-the-art facilities.",
        "Export figures improved 12% year-on-year according to commerce ministry data.",
    ]

    data = (
        [(text, 1) for text in fake_samples] +
        [(text, 0) for text in real_samples]
    )
    df = pd.DataFrame(data, columns=["text", "label"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"Demo dataset size: {len(df)} samples")
    return df


def load_kaggle_dataset() -> pd.DataFrame | None:
    """Try to load the full Kaggle dataset if available."""
    fake_path = os.path.join(DATA_DIR, "Fake.csv")
    real_path = os.path.join(DATA_DIR, "True.csv")

    if os.path.exists(fake_path) and os.path.exists(real_path):
        print("Loading Kaggle Fake News dataset...")
        fake_df = pd.read_csv(fake_path)
        real_df = pd.read_csv(real_path)

        fake_df["label"] = 1
        real_df["label"] = 0

        # Combine title and text
        for df in [fake_df, real_df]:
            df["text"] = df.get("title", "") + " " + df.get("text", "")

        combined = pd.concat([fake_df[["text", "label"]], real_df[["text", "label"]]])
        combined = combined.dropna(subset=["text"]).sample(frac=1, random_state=42)
        print(f"Kaggle dataset loaded: {len(combined)} samples")
        return combined

    return None


def train_naive_bayes(X_train, X_test, y_train, y_test):
    print("\n--- Training TF-IDF + Naive Bayes ---")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=50000,
            min_df=1,
            stop_words="english",
        )),
        ("clf", MultinomialNB(alpha=0.1)),
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))
    return pipeline, acc


def train_logistic_regression(X_train, X_test, y_train, y_test):
    print("\n--- Training TF-IDF + Logistic Regression ---")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=80000,
            min_df=1,
            stop_words="english",
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000, C=5.0,
            class_weight="balanced",
            solver="lbfgs",
        )),
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))
    return pipeline, acc


def main():
    # Try Kaggle dataset first, fall back to demo
    df = load_kaggle_dataset() or build_demo_dataset()

    X = df["text"].astype(str).values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training size: {len(X_train)}, Test size: {len(X_test)}")

    nb_model, nb_acc = train_naive_bayes(X_train, X_test, y_train, y_test)
    lr_model, lr_acc = train_logistic_regression(X_train, X_test, y_train, y_test)

    # Save best
    best_pipeline, best_acc, best_name = max(
        [(nb_model, nb_acc, "Naive Bayes"), (lr_model, lr_acc, "Logistic Regression")],
        key=lambda x: x[1]
    )
    print(f"\n✅ Best model: {best_name} ({best_acc:.4f})")
    path = os.path.join(MODEL_DIR, "fake_news_model.joblib")
    joblib.dump(best_pipeline, path)
    print(f"Model saved to {path}")

    # Test
    print("\n--- Sample Predictions ---")
    model = joblib.load(path)
    samples = [
        "SHOCKING: Scientists discover miracle cure that big pharma is hiding!",
        "The RBI governor confirmed inflation remains within the target range.",
        "Government cover-up exposed — deep state conspiracy revealed!",
        "Supreme Court announced verdict on landmark property rights case today.",
    ]
    preds = model.predict(samples)
    probs = model.predict_proba(samples)
    for text, pred, prob in zip(samples, preds, probs):
        label = "FAKE" if pred == 1 else "REAL"
        conf = max(prob) * 100
        print(f"[{label} {conf:.1f}%] {text[:70]}...")


if __name__ == "__main__":
    main()
