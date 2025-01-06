import nltk
import re
import hopsworks
import dotenv
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    matthews_corrcoef,
    classification_report
)

dotenv.load_dotenv()


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, stopwords=None):
        self.stopwords = set(stopwords) if stopwords else set()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self.clean_text(text) for text in X]

    def clean_text(self, text):
        # Remove special characters
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        # Remove stopwords
        return " ".join([word for word in text.lower().split() if word not in self.stopwords])


def get_training_data():
    project = hopsworks.login(api_key_value=os.environ.get("HOPSWORKS_KEY"))
    fs = project.get_feature_store(name="portuguese_lyrics_featurestore")
    return fs.get_feature_group("lyrics").read()


def main():
    nltk.download("stopwords")
    stopwords = nltk.corpus.stopwords.words("portuguese")

    pipeline = Pipeline(
        [
            ("preprocess", TextPreprocessor(stopwords=stopwords)),
            ("tfidf", TfidfVectorizer(max_features=5000)),
            ("model", LogisticRegression(class_weight="balanced")),
        ]
    )

    data = get_training_data()
    X, y = data["lyrics"], data["genre"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    with open("results/metrics.txt", "w") as f:
        f.write(f"Accuracy: {accuracy:.2f}\n")
        f.write(f"MCC: {mcc:.2f}\n")
        f.write(report)
    
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(12, 12))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=y.unique(), yticklabels=y.unique())
    plt.savefig("results/confusion_matrix.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
