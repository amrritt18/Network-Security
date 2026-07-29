import os
import sys
import json

import certifi
import pandas as pd
import pymongo
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Load environment variables
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL is not found in the .env file.")

# SSL Certificate for MongoDB Atlas
ca = certifi.where()


class NetworkDataExtract:
    def __init__(self):
        try:
            self.mongo_client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=ca
            )
            logging.info("MongoDB connection established successfully.")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_convertor(self, file_path: str):
        """
        Read CSV file and convert it into JSON records.
        """
        try:
            logging.info(f"Reading CSV file: {file_path}")

            data = pd.read_csv(file_path)

            data.reset_index(drop=True, inplace=True)

            records = json.loads(data.to_json(orient="records"))

            logging.info(f"Successfully converted {len(records)} records to JSON.")

            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database: str, collection: str):
        """
        Insert JSON records into MongoDB.
        """
        try:
            db = self.mongo_client[database]
            collection = db[collection]

            result = collection.insert_many(records)

            logging.info(
                f"Inserted {len(result.inserted_ids)} records into '{database}.{collection.name}'."
            )

            return len(result.inserted_ids)

        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    try:
        FILE_PATH = r"D:\MLOPS\Projects\NETWORK_SECURITY\Network_Data\phisingData.csv"
        DATABASE = "AMRITAI"
        COLLECTION = "NetworkData"

        network_obj = NetworkDataExtract()

        records = network_obj.csv_to_json_convertor(FILE_PATH)

        print(f"Total Records: {len(records)}")

        inserted_records = network_obj.insert_data_mongodb(
            records,
            DATABASE,
            COLLECTION,
        )

        print(f"Inserted {inserted_records} records successfully.")

    except Exception as e:
        raise NetworkSecurityException(e, sys)