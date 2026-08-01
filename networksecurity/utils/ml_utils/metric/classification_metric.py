import sys

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from networksecurity.entity.artifact_entity import (
    ClassificationMetricArtifact,
)

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging


def get_classification_score(
    y_true,
    y_pred,
) -> ClassificationMetricArtifact:
    """
    Calculate classification metrics.

    Parameters
    ----------
    y_true : array-like
        Actual target values.

    y_pred : array-like
        Predicted target values.

    Returns
    -------
    ClassificationMetricArtifact
    """

    try:

        logging.info(
            "Calculating classification metrics."
        )

        model_accuracy_score = accuracy_score(
            y_true,
            y_pred,
        )

        model_f1_score = f1_score(
            y_true,
            y_pred,
        )

        model_precision_score = precision_score(
            y_true,
            y_pred,
        )

        model_recall_score = recall_score(
            y_true,
            y_pred,
        )

        classification_metric = ClassificationMetricArtifact(

            accuracy_score=model_accuracy_score,

            f1_score=model_f1_score,

            precision_score=model_precision_score,

            recall_score=model_recall_score,
        )

        logging.info(
            f"Accuracy  : {model_accuracy_score:.4f}"
        )

        logging.info(
            f"F1 Score  : {model_f1_score:.4f}"
        )

        logging.info(
            f"Precision : {model_precision_score:.4f}"
        )

        logging.info(
            f"Recall    : {model_recall_score:.4f}"
        )

        return classification_metric

    except Exception as e:
        raise NetworkSecurityException(e, sys)