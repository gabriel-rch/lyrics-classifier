import hopsworks
import dotenv
import os
import wandb
import joblib
from utils import TextPreprocessor
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, matthews_corrcoef


dotenv.load_dotenv()


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


def train_pipeline(config, X_train, y_train):
    pipeline = Pipeline(
        [
            ("preprocess", TextPreprocessor()),
            ("tfidf", TfidfVectorizer(max_features=config["max_features"])),
            (
                "model",
                LogisticRegression(
                    solver=config["solver"],
                    C=config["C"],
                    class_weight=config["class_weight"],
                    random_state=1337,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    return pipeline


def train(config=None):
    with wandb.init(config=config):
        config = wandb.config

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
        pipeline = train_pipeline(config, X_train, y_train)
        y_pred = pipeline.predict(X_test)

        wandb.log({"accuracy": accuracy_score(y_test, y_pred)})
        wandb.log({"mcc": matthews_corrcoef(y_test, y_pred)})

        le = LabelEncoder().fit(y.unique())

        cm = wandb.plot.confusion_matrix(
            y_true=le.transform(y_test),
            preds=le.transform(y_pred),
            class_names=y.unique(),
        )

        wandb.log({"confusion_matrix": cm})


wandb.login(key=os.environ.get("WANDB_KEY"))
sweep_id = wandb.sweep(sweep_config, project="lyrics-classifier")
wandb.agent(sweep_id, train, count=60)

api = wandb.Api()
sweep = api.sweep(sweep_id)

best_run = sweep.best_run()
best_config = best_run.config

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
pipeline = train_pipeline(best_config, X_train, y_train)
joblib.dump(pipeline, "pipeline.pkl")

wandb.finish()
