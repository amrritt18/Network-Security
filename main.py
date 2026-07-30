import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    TrainingPipelineConfig,
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


def main():
    try:
        logging.info("Starting Network Security Training Pipeline")

        # Pipeline Configuration
        training_pipeline_config = TrainingPipelineConfig()

        # Data Ingestion Configuration
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config
        )

        # Data Ingestion Component
        data_ingestion = DataIngestion(data_ingestion_config)

        logging.info("Initiating Data Ingestion...")

        data_ingestion_artifact = (
            data_ingestion.initiate_data_ingestion()
        )

        logging.info("Data Ingestion Completed Successfully.")

        print("\nData Ingestion Artifact")
        print(data_ingestion_artifact)

    except Exception as e:
        logging.exception("Pipeline execution failed.")
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    main()