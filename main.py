import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


def main():
    try:
        logging.info("=" * 60)
        logging.info("Starting Network Security Training Pipeline")
        logging.info("=" * 60)

        # Pipeline Configuration
        
        training_pipeline_config = TrainingPipelineConfig()

        # Data Ingestion
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config
        )

        data_ingestion = DataIngestion(
            data_ingestion_config
        )

        logging.info("Starting Data Ingestion...")

        data_ingestion_artifact = (
            data_ingestion.initiate_data_ingestion()
        )

        logging.info("Data Ingestion Completed Successfully.")

        print("\nData Ingestion Artifact")
        print(data_ingestion_artifact)

        # Data Validation
        data_validation_config = DataValidationConfig(
            training_pipeline_config
        )

        data_validation = DataValidation(
            data_ingestion_artifact,
            data_validation_config,
        )

        logging.info("Starting Data Validation...")

        data_validation_artifact = (
            data_validation.initiate_data_validation()
        )

        logging.info("Data Validation Completed Successfully.")

        print("\nData Validation Artifact")
        print(data_validation_artifact)

        logging.info("=" * 60)
        logging.info("Pipeline Executed Successfully")
        logging.info("=" * 60)

        # Data Transformation

        data_transformation_config = DataTransformationConfig(
            training_pipeline_config
        )

        data_transformation = DataTransformation(
            data_validation_artifact,
            data_transformation_config,
        )

        logging.info("Starting Data Transformation...")

        data_transformation_artifact = (
            data_transformation.initiate_data_transformation()
        )

        logging.info("Data Transformation Completed Successfully.")

        print("\nData Transformation Artifact")
        print(data_transformation_artifact)


    except Exception as e:
        logging.exception("Pipeline execution failed.")
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    main()