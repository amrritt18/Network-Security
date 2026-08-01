import os
import sys

import certifi
import pandas as pd
import pymongo

from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

from uvicorn import run as app_run

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.pipeline.training_pipeline import TrainingPipeline

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)


load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

if not MONGO_DB_URL:
    raise ValueError(
        "MONGO_DB_URL is not found in the .env file."
    )


ca = certifi.where()


client = pymongo.MongoClient(
    MONGO_DB_URL,
    tlsCAFile=ca
)


database = client[
    DATA_INGESTION_DATABASE_NAME
]

collection = database[
    DATA_INGESTION_COLLECTION_NAME
]


app = FastAPI(
    title="Network Security API",
    description="Phishing Website Detection API",
    version="1.0.0",
)


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(
    directory="./templates"
)


@app.get("/")
async def index():

    return RedirectResponse(
        url="/docs"
    )


@app.get("/train")
async def train_route():

    try:

        logging.info(
            "Training request received."
        )

        training_pipeline = (
            TrainingPipeline()
        )

        model_trainer_artifact = (
            training_pipeline.run_pipeline()
        )

        logging.info(
            "Training completed successfully."
        )

        return {
            "message": "Training completed successfully",
            "model_path": (
                model_trainer_artifact
                .trained_model_file_path
            ),
        }

    except Exception as e:

        logging.exception(
            "Training failed."
        )

        raise NetworkSecurityException(
            e,
            sys
        )


@app.post("/predict")
async def predict_route(
    request: Request,
    file: UploadFile = File(...),
):

    try:

        logging.info(
            "Prediction request received."
        )

        df = pd.read_csv(
            file.file
        )

        logging.info(
            f"Prediction dataset shape: {df.shape}"
        )

        model_path = os.path.join(
            "final_model",
            "model.pkl"
        )

        network_model = load_object(
            file_path=model_path
        )

        y_pred = network_model.predict(
            df
        )

        df[
            "predicted_column"
        ] = y_pred

        os.makedirs(
            "prediction_output",
            exist_ok=True,
        )

        output_path = os.path.join(
            "prediction_output",
            "output.csv"
        )

        df.to_csv(
            output_path,
            index=False,
        )

        logging.info(
            f"Prediction output saved at {output_path}"
        )

        table_html = df.to_html(
            classes="table table-striped",
            index=False,
        )

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={
                "table": table_html
            },
        )

    except Exception as e:

        logging.exception(
            "Prediction failed."
        )

        raise NetworkSecurityException(
            e,
            sys
        )


if __name__ == "__main__":

    app_run(
        app,
        host="0.0.0.0",
        port=8000,
    )