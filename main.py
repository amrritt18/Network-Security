import sys

from networksecurity.pipeline.training_pipeline import (
    TrainingPipeline,
)

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging


def main():

    try:
        logging.info(
            "Starting Network Security Project."
        )

        training_pipeline = TrainingPipeline()

        model_trainer_artifact = (
            training_pipeline.run_pipeline()
        )

        print(
            "\nModel Trainer Artifact"
        )

        print(
            model_trainer_artifact
        )

        logging.info(
            "Network Security Project "
            "completed successfully."
        )

    except Exception as e:

        logging.exception(
            "Training failed."
        )

        raise NetworkSecurityException(
            e,
            sys
        )


if __name__ == "__main__":
    main()