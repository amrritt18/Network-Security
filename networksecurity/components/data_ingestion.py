import os
import sys

import certifi
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from networksecurity.entity.artifact_entity import DataIngestionArtifact
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Load environment variables
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

if MONGO_DB_URL is None:
    raise ValueError("MONGO_DB_URL is not found in the .env file.")

# SSL Certificate for MongoDB Atlas
ca = certifi.where()


class DataIngestion:
    """
    This class is responsible for reading data from MongoDB,
    creating the feature store, and splitting the data into
    training and testing datasets.
    """

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config

            self.mongo_client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=ca
            )

            logging.info("MongoDB connection established successfully.")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Export MongoDB collection as a Pandas DataFrame.
        """
        try:
            logging.info("Exporting collection from MongoDB.")

            database = self.mongo_client[
                self.data_ingestion_config.database_name
            ]

            collection = database[
                self.data_ingestion_config.collection_name
            ]

            records = list(collection.find())

            if len(records) == 0:
                raise Exception("MongoDB collection is empty.")

            dataframe = pd.DataFrame(records)

            if "_id" in dataframe.columns:
                dataframe.drop(columns=["_id"], inplace=True)

            dataframe.replace(
                {
                    "na": np.nan,
                    "NA": np.nan,
                    "Na": np.nan,
                    "null": np.nan,
                    "None": np.nan,
                },
                inplace=True,
            )

            logging.info(
                f"Successfully fetched {len(dataframe)} records from MongoDB."
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Save raw dataframe into the feature store.
        """
        try:
            feature_store_path = (
                self.data_ingestion_config.feature_store_file_path
            )

            os.makedirs(
                os.path.dirname(feature_store_path),
                exist_ok=True,
            )

            dataframe.to_csv(
                feature_store_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Feature Store created at: {feature_store_path}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Split dataframe into train and test datasets.
        """
        try:
            logging.info("Performing Train-Test Split.")

            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42,
            )

            train_path = (
                self.data_ingestion_config.training_file_path
            )

            test_path = (
                self.data_ingestion_config.testing_file_path
            )

            os.makedirs(
                os.path.dirname(train_path),
                exist_ok=True,
            )

            train_set.to_csv(
                train_path,
                index=False,
                header=True,
            )

            test_set.to_csv(
                test_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Training data saved at: {train_path}"
            )

            logging.info(
                f"Testing data saved at: {test_path}"
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Execute complete data ingestion pipeline.
        """
        try:
            logging.info("=" * 60)
            logging.info("Starting Data Ingestion Pipeline")
            logging.info("=" * 60)

            dataframe = self.export_collection_as_dataframe()

            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )

            logging.info("Data Ingestion Completed Successfully.")

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)