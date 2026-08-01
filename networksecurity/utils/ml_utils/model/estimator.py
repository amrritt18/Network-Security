import sys

import pandas as pd

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging


class NetworkModel:
    """
    Wrapper class that combines the preprocessing
    pipeline and trained machine learning model.
    """

    def __init__(
        self,
        preprocessor,
        model,
    ):
        try:

            self.preprocessor = preprocessor
            self.model = model

            logging.info(
                "NetworkModel initialized successfully."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict(
        self,
        X: pd.DataFrame,
    ):
        """
        Predict labels for the given input data.

        Parameters
        ----------
        X : pd.DataFrame
            Input features.

        Returns
        -------
        np.ndarray
            Predicted labels.
        """

        try:

            logging.info(
                "Applying preprocessing pipeline."
            )

            transformed_features = (
                self.preprocessor.transform(X)
            )

            logging.info(
                "Generating predictions."
            )

            predictions = self.model.predict(
                transformed_features
            )

            return predictions

        except Exception as e:
            raise NetworkSecurityException(e, sys)