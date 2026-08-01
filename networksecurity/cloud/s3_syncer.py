import os
import sys

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging


class S3Sync:

    def sync_folder_to_s3(
        self,
        folder: str,
        aws_bucket_url: str,
    ):
        try:

            command = (
                f'aws s3 sync "{folder}" "{aws_bucket_url}"'
            )

            logging.info(
                f"Executing command: {command}"
            )

            exit_code = os.system(command)

            if exit_code != 0:
                raise Exception(
                    "Failed to sync folder to S3."
                )

            logging.info(
                f"Successfully synced {folder} "
                f"to {aws_bucket_url}"
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def sync_folder_from_s3(
        self,
        folder: str,
        aws_bucket_url: str,
    ):
        try:

            os.makedirs(
                folder,
                exist_ok=True,
            )

            command = (
                f'aws s3 sync "{aws_bucket_url}" "{folder}"'
            )

            logging.info(
                f"Executing command: {command}"
            )

            exit_code = os.system(command)

            if exit_code != 0:
                raise Exception(
                    "Failed to sync folder from S3."
                )

            logging.info(
                f"Successfully synced {aws_bucket_url} "
                f"to {folder}"
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)