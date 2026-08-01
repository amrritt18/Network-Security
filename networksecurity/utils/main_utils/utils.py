import os
import sys
import pickle
from typing import Any, Dict

import numpy as np
import yaml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


# YAML Utilities

def read_yaml_file(file_path: str) -> Dict:
    """Read a YAML file and return its contents."""

    try:
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            return yaml.safe_load(yaml_file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(
    file_path: str,
    content: Any,
    replace: bool = False,
) -> None:
    """Write content into a YAML file."""

    try:

        if replace and os.path.exists(file_path):
            os.remove(file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# NumPy Utilities

def save_numpy_array_data(
    file_path: str,
    array: np.ndarray,
) -> None:
    """Save a NumPy array."""

    try:

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as file:
            np.save(file, array)

        logging.info(f"Numpy array saved to {file_path}")

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def load_numpy_array_data(
    file_path: str,
) -> np.ndarray:
    """Load a NumPy array."""

    try:

        with open(file_path, "rb") as file:
            return np.load(file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# Pickle Utilities

def save_object(
    file_path: str,
    obj: object,
) -> None:
    """Serialize a Python object."""

    try:

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as file:
            pickle.dump(obj, file)

        logging.info(f"Object saved to {file_path}")

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def load_object(
    file_path: str,
) -> object:
    """Load a serialized Python object."""

    try:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"{file_path} does not exist."
            )

        with open(file_path, "rb") as file:
            return pickle.load(file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# Model Evaluation

def evaluate_models(
    X_train,
    y_train,
    X_test,
    y_test,
    models: Dict,
    params: Dict,
):
    try:
        report = {}
        trained_models = {}

        for model_name, model in models.items():

            logging.info(
                f"Training model: {model_name}"
            )

            param_grid = params.get(
                model_name,
                {}
            )

            grid_search = GridSearchCV(
                estimator=model,
                param_grid=param_grid,
                cv=3,
                n_jobs=-1,
                scoring="accuracy",
            )

            grid_search.fit(
                X_train,
                y_train
            )

            best_model = (
                grid_search.best_estimator_
            )

            y_train_pred = best_model.predict(
                X_train
            )

            y_test_pred = best_model.predict(
                X_test
            )

            train_score = accuracy_score(
                y_train,
                y_train_pred
            )

            test_score = accuracy_score(
                y_test,
                y_test_pred
            )

            logging.info(
                f"{model_name} | "
                f"Train Accuracy: {train_score:.4f} | "
                f"Test Accuracy: {test_score:.4f}"
            )

            logging.info(
                f"{model_name} Best Parameters: "
                f"{grid_search.best_params_}"
            )

            report[model_name] = test_score

            trained_models[model_name] = (
                best_model
            )

        return report, trained_models

    except Exception as e:
        raise NetworkSecurityException(
            e,
            sys
        )