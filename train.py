import nltk
import hopsworks
import dotenv
import os
import wandb
import re
from unidecode import unidecode
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, matthews_corrcoef

dotenv.load_dotenv()

nltk.download("stopwords")
stopwords = nltk.corpus.stopwords.words("portuguese")

sweep_config = {
    "method": "random",  # Random search for hyperparameter tuning
    "metric": {
        "name": "accuracy",  # Evaluation metric to optimize
        "goal": "maximize",  # Maximize the accuracy
    },
    "parameters": {
        "max_features": {
            "distribution": "int_uniform",  # Number of features to use
            "min": 5000,
            "max": 20000,
        },
        "solver": {
            "values": ["lbfgs", "newton-cg", "sag", "saga"]  # Solvers for Logistic Regression
        },
        "C": {
            "distribution": "log_uniform",  # Regularization strength
            "min": 1e-2,
            "max": 2,
        },
        "class_weight": {
            "values": ["balanced", None]  # Class weights
        },
    },
}

project = hopsworks.login(api_key_value=os.environ.get("HOPSWORKS_KEY"))
fs = project.get_feature_store(name="portuguese_lyrics_featurestore")

data = fs.get_feature_group("lyrics").read()
X, y = data["lyrics"], data["genre"]


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, stopwords=None):
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
        text = re.sub(r'[^\w\s]', '', text)
        # Remove stopwords
        return " ".join([word for word in text.split() if word not in self.stopwords])


def train(config=None):
    with wandb.init(config=config):
        config = wandb.config

        pipeline = Pipeline(
            [
                ("preprocess", TextPreprocessor(stopwords=stopwords)),
                ("tfidf", TfidfVectorizer(max_features=config.max_features)),
                (
                    "model",
                    LogisticRegression(
                        solver=config.solver,
                        C=config.C,
                        class_weight=config.class_weight,
                    ),
                ),
            ]
        )

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        wandb.log({"accuracy": accuracy_score(y_test, y_pred)})
        wandb.log({"mcc": matthews_corrcoef(y_test, y_pred)})

        le = LabelEncoder().fit(y.unique())

        cm = wandb.plot.confusion_matrix(
            y_true=le.transform(y_test),
            preds= le.transform(y_pred),
            class_names=y.unique(),
        )

        wandb.log({"confusion_matrix": cm})


wandb.login(key=os.environ.get("WANDB_KEY"))
sweep_id = wandb.sweep(sweep_config, project="lyrics-classifier")
wandb.agent(sweep_id, train, count=5)

api = wandb.Api()
sweep = api.sweep(sweep_id)

best_run = sweep.best_run()
best_config = best_run.config

wandb.finish()

# with open("results/metrics.txt", "w") as f:
#     f.write(f"Accuracy: {accuracy:.2f}\n")
#     f.write(f"MCC: {mcc:.2f}\n")
#     f.write(report)
