import os
import sys
from urllib.parse import urlparse

import mlflow
import mlflow.sklearn
import numpy as np
from dotenv import load_dotenv

from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from networksecurity.entity.config_entity import (
    ModelTrainerConfig,
)

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging

from networksecurity.utils.main_utils.utils import (
    evaluate_models,
    load_numpy_array_data,
    load_object,
    save_object,
)

from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score,
)

from networksecurity.utils.ml_utils.model.estimator import (
    NetworkModel,
)

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_TRACKING_USERNAME = os.getenv("MLFLOW_TRACKING_USERNAME")
MLFLOW_TRACKING_PASSWORD = os.getenv("MLFLOW_TRACKING_PASSWORD")

if MLFLOW_TRACKING_URI:
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI

if MLFLOW_TRACKING_USERNAME:
    os.environ["MLFLOW_TRACKING_USERNAME"] = (
        MLFLOW_TRACKING_USERNAME
    )

if MLFLOW_TRACKING_PASSWORD:
    os.environ["MLFLOW_TRACKING_PASSWORD"] = (
        MLFLOW_TRACKING_PASSWORD
    )


class ModelTrainer:
    """
    Model Trainer Component

    Responsibilities
    ----------------
    1. Load transformed train/test arrays.
    2. Train multiple models.
    3. Perform hyperparameter tuning.
    4. Select the best model.
    5. Evaluate the best model.
    6. Log experiments to MLflow.
    7. Save trained model.
    """

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):

        try:

            self.model_trainer_config = (
                model_trainer_config
            )

            self.data_transformation_artifact = (
                data_transformation_artifact
            )

            logging.info(
                "ModelTrainer initialized successfully."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(
        self,
        model,
        classification_metric,
    ) -> None:
        """
        Log model and metrics to MLflow.
        """

        try:

            mlflow.set_tracking_uri(
                os.getenv("MLFLOW_TRACKING_URI")
            )

            tracking_url_type_store = urlparse(
                mlflow.get_tracking_uri()
            ).scheme

            with mlflow.start_run():

                mlflow.log_metric(
                    "accuracy",
                    classification_metric.accuracy_score,
                )

                mlflow.log_metric(
                    "f1_score",
                    classification_metric.f1_score,
                )

                mlflow.log_metric(
                    "precision_score",
                    classification_metric.precision_score,
                )

                mlflow.log_metric(
                    "recall_score",
                    classification_metric.recall_score,
                )

                if tracking_url_type_store != "file":

                    mlflow.sklearn.log_model(
                        sk_model=model,
                        name="model",
                        registered_model_name=model.__class__.__name__,
                    )

                else:

                    mlflow.sklearn.log_model(
                        sk_model=model,
                        name="model",
                    )

                logging.info(
                    "MLflow tracking completed successfully."
                )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(
            self,
            X_train,
            y_train,
            X_test,
            y_test,
        ) -> ModelTrainerArtifact:

        try:

            logging.info("Starting model training.")

            models = {

                "Random Forest": RandomForestClassifier(),

                "Decision Tree": DecisionTreeClassifier(),

                "Gradient Boosting": GradientBoostingClassifier(),

                "Logistic Regression": LogisticRegression(
                    max_iter=1000
                ),

                "AdaBoost": AdaBoostClassifier(),
            }

            params = {

                "Decision Tree": {

                    "criterion": [
                        "gini",
                        "entropy",
                        "log_loss",
                    ],
                },

                "Random Forest": {

                    "n_estimators": [
                        8,
                        16,
                        32,
                        64,
                        128,
                        256,
                    ],
                },

                "Gradient Boosting": {

                    "learning_rate": [
                        0.1,
                        0.05,
                        0.01,
                        0.001,
                    ],

                    "subsample": [
                        0.6,
                        0.7,
                        0.8,
                        0.9,
                        1.0,
                    ],

                    "n_estimators": [
                        8,
                        16,
                        32,
                        64,
                        128,
                        256,
                    ],
                },

                "Logistic Regression": {},

                "AdaBoost": {

                    "learning_rate": [
                        0.1,
                        0.01,
                        0.001,
                    ],

                    "n_estimators": [
                        8,
                        16,
                        32,
                        64,
                        128,
                        256,
                    ],
                },
            }

            logging.info(
                "Evaluating all machine learning models."
            )

            model_report, trained_models = evaluate_models(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models,
                params=params,
            )

            logging.info(
                f"Model Report : {model_report}"
            )

            best_model_name = max(
                model_report,
                key=model_report.get,
            )

            best_model_score = model_report[
                best_model_name
            ]

            best_model = trained_models[
                best_model_name
            ]

            logging.info(
                f"Best Model : {best_model_name}"
            )

            logging.info(
                f"Best Score : {best_model_score}"
            )

            if (
                best_model_score
                < self.model_trainer_config.expected_accuracy
            ):

                raise Exception(
                    "No suitable model found."
                )

            y_train_pred = best_model.predict(
                X_train
            )

            y_test_pred = best_model.predict(
                X_test
            )

            train_metric = (
                get_classification_score(

                    y_true=y_train,

                    y_pred=y_train_pred,
                )
            )

            test_metric = (
                get_classification_score(

                    y_true=y_test,

                    y_pred=y_test_pred,
                )
            )

            logging.info(
                f"Train Metrics : {train_metric}"
            )

            logging.info(
                f"Test Metrics : {test_metric}"
            )

            metric_difference = abs(

                train_metric.f1_score

                - test_metric.f1_score
            )

            if (
                metric_difference
                > self.model_trainer_config.overfitting_underfitting_threshold
            ):

                raise Exception(
                    "Model is overfitting or underfitting."
                )

            logging.info(
                "Logging experiment to MLflow."
            )

            self.track_mlflow(
                best_model,
                test_metric,
            )

            logging.info(
                "Loading preprocessing object."
            )

            preprocessor = load_object(
                file_path=self.data_transformation_artifact.transformed_object_file_path
            )

            logging.info(
                "Creating NetworkModel object."
            )

            network_model = NetworkModel(
                preprocessor=preprocessor,
                model=best_model,
            )

            model_dir = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            )

            os.makedirs(
                model_dir,
                exist_ok=True,
            )

            logging.info(
                "Saving trained model."
            )

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=network_model,
            )

            os.makedirs(
                "final_model",
                exist_ok=True,
            )

            save_object(
                file_path=os.path.join(
                    "final_model",
                    "model.pkl",
                ),
                obj=network_model,
            )

            logging.info(
                "Model saved successfully."
            )

            model_trainer_artifact = (
                ModelTrainerArtifact(

                    trained_model_file_path=
                    self.model_trainer_config.trained_model_file_path,

                    train_metric_artifact=train_metric,

                    test_metric_artifact=test_metric,
                )
            )

            logging.info(
                f"Model Trainer Artifact : {model_trainer_artifact}"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(
        self,
    ) -> ModelTrainerArtifact:

        try:

            logging.info(
                "Loading transformed training and testing arrays."
            )

            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )

            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            X_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            X_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            logging.info(
                f"Training Shape : {X_train.shape}"
            )

            logging.info(
                f"Testing Shape : {X_test.shape}"
            )

            model_trainer_artifact = self.train_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            )

            logging.info(
                "Model Training completed successfully."
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)