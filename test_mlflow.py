import os

import mlflow
from dotenv import load_dotenv

load_dotenv()

tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

mlflow.set_tracking_uri(tracking_uri)

mlflow.set_experiment(
    "Network-Security-Test"
)

with mlflow.start_run():

    mlflow.log_param(
        "model_name",
        "RandomForestClassifier"
    )

    mlflow.log_param(
        "n_estimators",
        100
    )

    mlflow.log_metric(
        "accuracy",
        0.97
    )

    mlflow.log_metric(
        "precision",
        0.96
    )

    mlflow.log_metric(
        "recall",
        0.98
    )

    mlflow.log_metric(
        "f1_score",
        0.97
    )

    print("Experiment logged successfully!")

    print(
        "Run ID:",
        mlflow.active_run().info.run_id
    )