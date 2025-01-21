import re
import nltk
from sklearn.base import BaseEstimator, TransformerMixin
from unidecode import unidecode


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        nltk.download("stopwords")
        stopwords = nltk.corpus.stopwords.words("portuguese")
        self.stopwords = set(stopwords) if stopwords else set()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self.clean_text(text) for text in X]

    def clean_text(self, text: str):
        # To lowercase
        text = text.lower()
        # Normalize
        text = unidecode(text)
        # Remove ponctuation
        text = re.sub(r"[^\w\s]", "", text)
        # Remove stopwords
        return " ".join([word for word in text.split() if word not in self.stopwords])