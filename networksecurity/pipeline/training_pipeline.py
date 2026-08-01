import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from networksecurity.constants.training_pipeline import (
    TRAINING_BUCKET_NAME,
)

from networksecurity.cloud.s3_syncer import S3Sync


class TrainingPipeline:

    def __init__(self):
        try:
            logging.info(
                "Initializing Training Pipeline."
            )

            self.training_pipeline_config = (
                TrainingPipelineConfig()
            )

            self.s3_sync = S3Sync()

            logging.info(
                "Training Pipeline initialized successfully."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def start_data_ingestion(
        self,
    ) -> DataIngestionArtifact:

        try:
            logging.info(
                "Starting Data Ingestion."
            )

            data_ingestion_config = (
                DataIngestionConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_ingestion = DataIngestion(
                data_ingestion_config=
                data_ingestion_config
            )

            data_ingestion_artifact = (
                data_ingestion.initiate_data_ingestion()
            )

            logging.info(
                f"Data Ingestion completed. "
                f"Artifact: {data_ingestion_artifact}"
            )

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def start_data_validation(
        self,
        data_ingestion_artifact:
        DataIngestionArtifact,
    ) -> DataValidationArtifact:

        try:
            logging.info(
                "Starting Data Validation."
            )

            data_validation_config = (
                DataValidationConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_validation = DataValidation(
                data_ingestion_artifact=
                data_ingestion_artifact,

                data_validation_config=
                data_validation_config,
            )

            data_validation_artifact = (
                data_validation
                .initiate_data_validation()
            )

            logging.info(
                f"Data Validation completed. "
                f"Artifact: {data_validation_artifact}"
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def start_data_transformation(
        self,
        data_validation_artifact:
        DataValidationArtifact,
    ) -> DataTransformationArtifact:

        try:
            logging.info(
                "Starting Data Transformation."
            )

            data_transformation_config = (
                DataTransformationConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            data_transformation = (
                DataTransformation(
                    data_validation_artifact=
                    data_validation_artifact,

                    data_transformation_config=
                    data_transformation_config,
                )
            )

            data_transformation_artifact = (
                data_transformation
                .initiate_data_transformation()
            )

            logging.info(
                f"Data Transformation completed. "
                f"Artifact: "
                f"{data_transformation_artifact}"
            )

            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def start_model_trainer(
        self,
        data_transformation_artifact:
        DataTransformationArtifact,
    ) -> ModelTrainerArtifact:

        try:
            logging.info(
                "Starting Model Trainer."
            )

            model_trainer_config = (
                ModelTrainerConfig(
                    training_pipeline_config=
                    self.training_pipeline_config
                )
            )

            model_trainer = ModelTrainer(
                model_trainer_config=
                model_trainer_config,

                data_transformation_artifact=
                data_transformation_artifact,
            )

            model_trainer_artifact = (
                model_trainer
                .initiate_model_trainer()
            )

            logging.info(
                f"Model Training completed. "
                f"Artifact: {model_trainer_artifact}"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def sync_artifact_dir_to_s3(
        self,
    ) -> None:

        try:
            logging.info(
                "Starting artifact synchronization "
                "with S3."
            )

            aws_bucket_url = (
                f"s3://{TRAINING_BUCKET_NAME}"
                f"/artifact/"
                f"{self.training_pipeline_config.timestamp}"
            )

            logging.info(
                f"Uploading artifacts to: "
                f"{aws_bucket_url}"
            )

            self.s3_sync.sync_folder_to_s3(
                folder=
                self.training_pipeline_config.artifact_dir,

                aws_bucket_url=
                aws_bucket_url,
            )

            logging.info(
                "Artifacts synchronized "
                "with S3 successfully."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def sync_saved_model_dir_to_s3(
        self,
    ) -> None:

        try:
            logging.info(
                "Starting final model "
                "synchronization with S3."
            )

            aws_bucket_url = (
                f"s3://{TRAINING_BUCKET_NAME}"
                f"/final_model/"
                f"{self.training_pipeline_config.timestamp}"
            )

            logging.info(
                f"Uploading final model to: "
                f"{aws_bucket_url}"
            )

            self.s3_sync.sync_folder_to_s3(
                folder=
                self.training_pipeline_config.model_dir,

                aws_bucket_url=
                aws_bucket_url,
            )

            logging.info(
                "Final model synchronized "
                "with S3 successfully."
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def run_pipeline(
        self,
    ) -> ModelTrainerArtifact:

        try:
            logging.info(
                "Starting Network Security "
                "Training Pipeline."
            )

            # Data Ingestion

            data_ingestion_artifact = (
                self.start_data_ingestion()
            )

            # Data Validation

            data_validation_artifact = (
                self.start_data_validation(
                    data_ingestion_artifact=
                    data_ingestion_artifact
                )
            )

            # Data Transformation

            data_transformation_artifact = (
                self.start_data_transformation(
                    data_validation_artifact=
                    data_validation_artifact
                )
            )

            # Model Training

            model_trainer_artifact = (
                self.start_model_trainer(
                    data_transformation_artifact=
                    data_transformation_artifact
                )
            )

            logging.info(
                "All training components "
                "completed successfully."
            )

            # Upload pipeline artifacts to S3

            self.sync_artifact_dir_to_s3()

            # Upload final model to S3

            self.sync_saved_model_dir_to_s3()

            logging.info(
                "Network Security Training "
                "Pipeline completed successfully."
            )

            return model_trainer_artifact

        except Exception as e:
            logging.exception(
                "Training Pipeline failed."
            )

            raise NetworkSecurityException(
                e,
                sys
            )