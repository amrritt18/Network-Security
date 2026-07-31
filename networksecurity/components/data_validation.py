import os
import sys
from typing import List

import pandas as pd
from scipy.stats import ks_2samp
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
)
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import (
    read_yaml_file,
    write_yaml_file,
)


class DataValidation:
    """
    ===========================================================================
                        Data Validation Component

    Responsibilities
    ----------------
    1. Read Train/Test datasets
    2. Validate schema
    3. Validate column names
    4. Validate datatypes
    5. Validate target column
    6. Validate missing columns
    7. Validate extra columns
    8. Validate null values
    9. Validate duplicate rows
    10. Detect dataset drift
    ===========================================================================

    """

    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig,
    ):

        try:

            logging.info("Initializing Data Validation Component.")

            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config

            self.schema_config = read_yaml_file(
                SCHEMA_FILE_PATH
            )

            logging.info("Schema loaded successfully.")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
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

            logging.info(f"Reading dataset : {file_path}")

            dataframe = pd.read_csv(file_path)

            logging.info(
                f"Dataset Shape : {dataframe.shape}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_schema(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate schema.

        Checks

        • Missing Columns

        • Extra Columns

        Returns
        -------
        bool
        """

        try:

            expected_columns = list(self.schema_config["columns"].keys())

            actual_columns = list(
                dataframe.columns
            )

            missing_columns = [
                col
                for col in expected_columns
                if col not in actual_columns
            ]

            extra_columns = [
                col
                for col in actual_columns
                if col not in expected_columns
            ]

            logging.info(
                f"Expected Columns : {len(expected_columns)}"
            )

            logging.info(
                f"Actual Columns : {len(actual_columns)}"
            )

            if missing_columns:

                logging.error(
                    f"Missing Columns : {missing_columns}"
                )

            if extra_columns:

                logging.error(
                    f"Extra Columns : {extra_columns}"
                )

            if missing_columns or extra_columns:

                return False

            logging.info("Schema Validation Passed.")

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_target_column(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate Target Column.
        """

        try:

            target_column = self.schema_config["target_column"]

            if target_column not in dataframe.columns:

                logging.error(
                    f"Target Column '{target_column}' not found."
                )

                return False

            logging.info(
                "Target Column Validation Passed."
            )

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_datatypes(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate dataframe datatypes.
        """

        try:

            expected_schema = self.schema_config["columns"]

            validation_status = True

            for column, expected_dtype in expected_schema.items():

                actual_dtype = str(
                    dataframe[column].dtype
                )

                if actual_dtype != expected_dtype:

                    validation_status = False

                    logging.warning(
                        f"{column} -> "
                        f"Expected : {expected_dtype}, "
                        f"Found : {actual_dtype}"
                    )

            if validation_status:

                logging.info(
                    "Datatype Validation Passed."
                )

            return validation_status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_missing_values(
        self,
        dataframe: pd.DataFrame,
    ):
        """
        Check missing values.
        """

        try:

            logging.info(
                "Checking Missing Values..."
            )

            missing_percentage = (
                dataframe
                .isnull()
                .mean()
                * 100
            )

            missing_percentage = (
                missing_percentage[
                    missing_percentage > 0
                ]
            )

            if len(missing_percentage) == 0:

                logging.info(
                    "No Missing Values Found."
                )

                return

            for column, value in missing_percentage.items():

                logging.warning(
                    f"{column} -> {round(value,2)}%"
                )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_duplicate_rows(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate duplicate rows in dataset.

        Returns
        -------
        bool
            True if no duplicates are found.
        """

        try:

            duplicate_count = dataframe.duplicated().sum()

            logging.info(
                f"Duplicate Rows Found : {duplicate_count}"
            )

            if duplicate_count > 0:

                logging.warning(
                    f"{duplicate_count} duplicate rows detected."
                )

                return False

            logging.info(
                "Duplicate Validation Passed."
            )

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_numerical_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> List[str]:
        """
        Return all numerical columns.

        Raises an exception if no numerical columns exist.
        """

        try:

            numeric_columns = list(
                dataframe.select_dtypes(
                    include=["number"]
                ).columns
            )

            if len(numeric_columns) == 0:

                raise Exception(
                    "No numerical columns found."
                )

            logging.info(
                f"Numerical Columns : {numeric_columns}"
            )

            return numeric_columns

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_same_numeric_columns(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> bool:
        """
        Ensure both datasets contain
        the same numerical columns.
        """

        try:

            train_columns = set(
                self.validate_numerical_columns(train_df)
            )

            test_columns = set(
                self.validate_numerical_columns(test_df)
            )

            if train_columns != test_columns:

                logging.error(
                    "Train and Test numerical columns differ."
                )

                logging.error(
                    f"Train : {train_columns}"
                )

                logging.error(
                    f"Test : {test_columns}"
                )

                return False

            logging.info(
                "Numerical Column Validation Passed."
            )

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold: float = 0.05,
    ) -> bool:
        """
        Detect dataset drift using
        Kolmogorov-Smirnov Test.
        """

        try:

            logging.info(
                "Starting Dataset Drift Detection."
            )

            status = True

            report = {}

            numeric_columns = self.validate_numerical_columns(
                base_df
            )

            for column in numeric_columns:

                base_data = base_df[column].dropna()

                current_data = current_df[column].dropna()

                ks_result = ks_2samp(
                    base_data,
                    current_data,
                )

                p_value = float(
                    ks_result.pvalue
                )

                statistic = float(
                    ks_result.statistic
                )

                drift_found = bool(
                    p_value < threshold
                )

                if drift_found:

                    status = False

                report[column] = {

                    "ks_statistic": statistic,

                    "p_value": p_value,

                    "threshold": threshold,

                    "drift_status": drift_found

                }

            drift_report_path = (
                self.data_validation_config
                .drift_report_file_path
            )

            os.makedirs(
                os.path.dirname(
                    drift_report_path
                ),
                exist_ok=True,
            )

            write_yaml_file(
                file_path=drift_report_path,
                content=report,
            )

            logging.info(
                f"Drift Report Saved : {drift_report_path}"
            )

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_dataset_shape(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> bool:
        """
        Validate train and test datasets
        contain at least one row.
        """

        try:

            logging.info(
                f"Train Shape : {train_df.shape}"
            )

            logging.info(
                f"Test Shape : {test_df.shape}"
            )

            if train_df.empty:

                raise Exception(
                    "Training dataset is empty."
                )

            if test_df.empty:

                raise Exception(
                    "Testing dataset is empty."
                )

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def log_validation_summary(
        self,
        validation_status: bool,
    ):

        try:

            logging.info("=" * 60)

            if validation_status:

                logging.info(
                    "Data Validation PASSED."
                )

            else:

                logging.warning(
                    "Data Validation FAILED."
                )

            logging.info("=" * 60)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(
        self,
    ) -> DataValidationArtifact:
        """
        Execute complete Data Validation Pipeline.

        Returns
        -------
        DataValidationArtifact
        """

        try:

            logging.info("=" * 70)
            logging.info("Starting Data Validation Pipeline")
            logging.info("=" * 70)

            # ==========================================================
            # Read Train & Test Data
            # ==========================================================

            train_df = self.read_data(
                self.data_ingestion_artifact.trained_file_path
            )

            test_df = self.read_data(
                self.data_ingestion_artifact.test_file_path
            )

            # ==========================================================
            # Dataset Shape Validation
            # ==========================================================

            self.validate_dataset_shape(
                train_df=train_df,
                test_df=test_df,
            )

            # ==========================================================
            # Schema Validation
            # ==========================================================

            if not self.validate_schema(train_df):

                raise Exception(
                    "Training dataset schema validation failed."
                )

            if not self.validate_schema(test_df):

                raise Exception(
                    "Testing dataset schema validation failed."
                )

            # ==========================================================
            # Target Column Validation
            # ==========================================================

            if not self.validate_target_column(train_df):

                raise Exception(
                    "Target column missing in Training Dataset."
                )

            if not self.validate_target_column(test_df):

                raise Exception(
                    "Target column missing in Testing Dataset."
                )

            # ==========================================================
            # Datatype Validation
            # ==========================================================

            if not self.validate_datatypes(train_df):

                raise Exception(
                    "Training dataset datatype validation failed."
                )

            if not self.validate_datatypes(test_df):

                raise Exception(
                    "Testing dataset datatype validation failed."
                )

            # ==========================================================
            # Missing Value Validation
            # ==========================================================

            self.validate_missing_values(train_df)

            self.validate_missing_values(test_df)

            # ==========================================================
            # Duplicate Validation
            # ==========================================================

            train_duplicate_status = self.validate_duplicate_rows(
                train_df
            )

            test_duplicate_status = self.validate_duplicate_rows(
                test_df
            )

            if not train_duplicate_status:

                logging.warning(
                    "Training dataset contains duplicate rows."
                )

            if not test_duplicate_status:

                logging.warning(
                    "Testing dataset contains duplicate rows."
                )

            # ==========================================================
            # Numerical Column Validation
            # ==========================================================

            if not self.validate_same_numeric_columns(
                train_df=train_df,
                test_df=test_df,
            ):

                raise Exception(
                    "Numerical column validation failed."
                )

            # ==========================================================
            # Dataset Drift Detection
            # ==========================================================

            validation_status = self.detect_dataset_drift(
                base_df=train_df,
                current_df=test_df,
            )

            # ==========================================================
            # Save Valid / Invalid Dataset
            # ==========================================================

            if validation_status:

                logging.info(
                    "Dataset Drift Not Detected."
                )

                train_path = (
                    self.data_validation_config.valid_train_file_path
                )

                test_path = (
                    self.data_validation_config.valid_test_file_path
                )

            else:

                logging.warning(
                    "Dataset Drift Detected."
                )

                train_path = (
                    self.data_validation_config.invalid_train_file_path
                )

                test_path = (
                    self.data_validation_config.invalid_test_file_path
                )

            os.makedirs(
                os.path.dirname(train_path),
                exist_ok=True,
            )

            train_df.to_csv(
                train_path,
                index=False,
                header=True,
            )

            test_df.to_csv(
                test_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Train Dataset Saved : {train_path}"
            )

            logging.info(
                f"Test Dataset Saved : {test_path}"
            )

            # ==========================================================
            # Validation Summary
            # ==========================================================

            self.log_validation_summary(
                validation_status
            )

            # ==========================================================
            # Artifact Creation
            # ==========================================================

            data_validation_artifact = (
                DataValidationArtifact(

                    validation_status=validation_status,

                    valid_train_file_path=(
                        self.data_validation_config.valid_train_file_path
                    ),

                    valid_test_file_path=(
                        self.data_validation_config.valid_test_file_path
                    ),

                    invalid_train_file_path=(
                        self.data_validation_config.invalid_train_file_path
                    ),

                    invalid_test_file_path=(
                        self.data_validation_config.invalid_test_file_path
                    ),

                    drift_report_file_path=(
                        self.data_validation_config.drift_report_file_path
                    ),
                )
            )

            logging.info("=" * 70)
            logging.info("Data Validation Pipeline Completed Successfully.")
            logging.info("=" * 70)

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)