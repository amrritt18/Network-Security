import os
import sys

import numpy as np
import pandas as pd

from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constants.training_pipeline import (
    TARGET_COLUMN,
    DATA_TRANSFORMATION_IMPUTER_PARAMS,
)

from networksecurity.entity.artifact_entity import (
    DataValidationArtifact,
    DataTransformationArtifact,
)

from networksecurity.entity.config_entity import (
    DataTransformationConfig,
)

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging

from networksecurity.utils.main_utils.utils import (
    save_numpy_array_data,
    save_object,
)


class DataTransformation:
    """
    Data Transformation Component

    Responsibilities
    ----------------
    1. Read validated train and test data.
    2. Create preprocessing pipeline.
    3. Fit preprocessing on train data.
    4. Transform train and test data.
    5. Save transformed arrays.
    6. Save preprocessing object.
    """

    def __init__(
        self,
        data_validation_artifact: DataValidationArtifact,
        data_transformation_config: DataTransformationConfig,
    ):

        try:

            self.data_validation_artifact = (
                data_validation_artifact
            )

            self.data_transformation_config = (
                data_transformation_config
            )

            logging.info(
                "DataTransformation component initialized."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(
        file_path: str,
    ) -> pd.DataFrame:
        """
        Read CSV file.

        Parameters
        ----------
        file_path : str

        Returns
        -------
        pd.DataFrame
        """

        try:

            logging.info(
                f"Reading file : {file_path}"
            )

            dataframe = pd.read_csv(file_path)

            logging.info(
                f"Data Shape : {dataframe.shape}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_data_transformer_object(
        self,
    ) -> Pipeline:
        """
        Create preprocessing pipeline.

        Current Pipeline
        ----------------
        KNNImputer

        Returns
        -------
        Pipeline
        """

        try:

            logging.info(
                "Creating preprocessing pipeline."
            )

            imputer = KNNImputer(
                **DATA_TRANSFORMATION_IMPUTER_PARAMS
            )

            logging.info(
                f"KNNImputer Parameters : "
                f"{DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )

            preprocessing_pipeline = Pipeline(
                steps=[
                    (
                        "imputer",
                        imputer,
                    ),
                ]
            )

            logging.info(
                "Preprocessing pipeline created successfully."
            )

            return preprocessing_pipeline

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(
        self,
    ) -> DataTransformationArtifact:
        """
        Execute complete data transformation pipeline.

        Steps
        -----
        1. Read validated train and test datasets.
        2. Separate input features and target.
        3. Fit preprocessing pipeline.
        4. Transform train and test datasets.
        5. Save transformed datasets.
        6. Save preprocessing object.
        7. Return DataTransformationArtifact.
        """

        try:

            logging.info("=" * 70)
            logging.info("Starting Data Transformation Pipeline")
            logging.info("=" * 70)

            # Read Validated Data

            logging.info("Reading validated training dataset.")

            train_df = self.read_data(
                self.data_validation_artifact.valid_train_file_path
            )

            logging.info("Reading validated testing dataset.")

            test_df = self.read_data(
                self.data_validation_artifact.valid_test_file_path
            )

            logging.info(
                f"Training Dataset Shape : {train_df.shape}"
            )

            logging.info(
                f"Testing Dataset Shape : {test_df.shape}"
            )

            # Validate Target Column

            if TARGET_COLUMN not in train_df.columns:
                raise Exception(
                    f"{TARGET_COLUMN} not found in training dataframe."
                )

            if TARGET_COLUMN not in test_df.columns:
                raise Exception(
                    f"{TARGET_COLUMN} not found in testing dataframe."
                )

            # Split Input Features and Target

            input_feature_train_df = train_df.drop(
                columns=[TARGET_COLUMN],
                axis=1,
            )

            target_feature_train_df = train_df[
                TARGET_COLUMN
            ]

            input_feature_test_df = test_df.drop(
                columns=[TARGET_COLUMN],
                axis=1,
            )

            target_feature_test_df = test_df[
                TARGET_COLUMN
            ]

            # Convert Target Labels
            # (-1 -> 0)
   
            target_feature_train_df = (
                target_feature_train_df.replace(-1, 0)
            )

            target_feature_test_df = (
                target_feature_test_df.replace(-1, 0)
            )

            logging.info(
                "Target labels converted successfully."
            )

            # Create Preprocessing Pipeline

            preprocessing_pipeline = (
                self.get_data_transformer_object()
            )

            logging.info(
                "Fitting preprocessing pipeline."
            )

            preprocessing_object = (
                preprocessing_pipeline.fit(
                    input_feature_train_df
                )
            )

            # Transform Train Dataset

            transformed_train_features = (
                preprocessing_object.transform(
                    input_feature_train_df
                )
            )

            # Transform Test Dataset

            transformed_test_features = (
                preprocessing_object.transform(
                    input_feature_test_df
                )
            )

            logging.info(
                "Train and Test datasets transformed successfully."
            )

            # Create Final NumPy Arrays

            train_arr = np.c_[
                transformed_train_features,
                np.array(target_feature_train_df),
            ]

            test_arr = np.c_[
                transformed_test_features,
                np.array(target_feature_test_df),
            ]

            logging.info(
                f"Transformed Training Array Shape : {train_arr.shape}"
            )

            logging.info(
                f"Transformed Testing Array Shape : {test_arr.shape}"
            )

            # Save Transformed Arrays

            logging.info(
                "Saving transformed training numpy array."
            )

            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=train_arr,
            )

            logging.info(
                "Saving transformed testing numpy array."
            )

            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_test_file_path,
                array=test_arr,
            )

            # Save Preprocessing Object

            logging.info(
                "Saving preprocessing object."
            )

            save_object(
                file_path=self.data_transformation_config.transformed_object_file_path,
                obj=preprocessing_object,
            )

            # Save Deployment Copy

            final_model_dir = "final_model"

            os.makedirs(
                final_model_dir,
                exist_ok=True,
            )

            final_preprocessor_path = os.path.join(
                final_model_dir,
                "preprocessor.pkl",
            )

            save_object(
                file_path=final_preprocessor_path,
                obj=preprocessing_object,
            )

            logging.info(
                f"Preprocessor saved at : {final_preprocessor_path}"
            )

            # Create Artifact

            data_transformation_artifact = (
                DataTransformationArtifact(

                    transformed_object_file_path=
                    self.data_transformation_config.transformed_object_file_path,

                    transformed_train_file_path=
                    self.data_transformation_config.transformed_train_file_path,

                    transformed_test_file_path=
                    self.data_transformation_config.transformed_test_file_path,
                )
            )

            logging.info("=" * 70)
            logging.info(
                "Data Transformation Pipeline Completed Successfully."
            )
            logging.info("=" * 70)

            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)