import os
import sys

import certifi
import pandas as pd
import pymongo

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Request,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from uvicorn import run as app_run

from networksecurity.exception.exception import (
    NetworkSecurityException,
)

from networksecurity.logging.logger import logging

from networksecurity.pipeline.training_pipeline import (
    TrainingPipeline,
)

from networksecurity.utils.main_utils.utils import (
    load_object,
)

from networksecurity.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)


load_dotenv()


MONGO_DB_URL = os.getenv(
    "MONGO_DB_URL"
)


if not MONGO_DB_URL:
    raise ValueError(
        "MONGO_DB_URL is not found in the .env file."
    )


ca = certifi.where()


client = pymongo.MongoClient(
    MONGO_DB_URL,
    tlsCAFile=ca,
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
async def index(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
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
            "message": (
                "Training completed successfully"
            ),

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
            sys,
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


        # Check CSV file

        if not file.filename.lower().endswith(
            ".csv"
        ):

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": (
                        "Please upload a valid CSV file."
                    )
                },
            )


        # Read uploaded CSV

        df = pd.read_csv(
            file.file
        )


        logging.info(
            f"Prediction dataset shape: {df.shape}"
        )


        # Check empty dataset

        if df.empty:

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": (
                        "Uploaded CSV file is empty."
                    )
                },
            )


        # Model path

        model_path = os.path.join(
            "final_model",
            "model.pkl",
        )


        # Check model exists

        if not os.path.exists(
            model_path
        ):

            raise FileNotFoundError(
                f"Model not found at {model_path}"
            )


        # Load trained NetworkModel

        network_model = load_object(
            file_path=model_path
        )


        logging.info(
            "Model loaded successfully."
        )


        # Perform prediction

        y_pred = network_model.predict(
            df
        )


        logging.info(
            "Prediction completed successfully."
        )


        # Store raw prediction temporarily

        df["Prediction_Code"] = y_pred


        # Convert prediction into readable labels

        df["Prediction"] = (
            df["Prediction_Code"].map(
                {
                    0: "Legitimate",
                    1: "Phishing",
                    0.0: "Legitimate",
                    1.0: "Phishing",
                }
            )
        )


        # Remove raw prediction column

        df.drop(
            columns=[
                "Prediction_Code"
            ],
            inplace=True,
        )


        # Calculate total records

        total_records = len(
            df
        )


        # Count legitimate predictions

        legitimate_count = int(
            (
                df["Prediction"]
                == "Legitimate"
            ).sum()
        )


        # Count phishing predictions

        phishing_count = int(
            (
                df["Prediction"]
                == "Phishing"
            ).sum()
        )


        # Calculate legitimate percentage

        legitimate_percentage = round(
            (
                legitimate_count
                / total_records
            )
            * 100,
            2,
        )


        # Calculate phishing percentage

        phishing_percentage = round(
            (
                phishing_count
                / total_records
            )
            * 100,
            2,
        )


        logging.info(
            f"Total Records: {total_records}"
        )

        logging.info(
            f"Legitimate: {legitimate_count}"
        )

        logging.info(
            f"Phishing: {phishing_count}"
        )


        # Create prediction output folder

        os.makedirs(
            "prediction_output",
            exist_ok=True,
        )


        # Prediction output path

        output_path = os.path.join(
            "prediction_output",
            "output.csv",
        )


        # Save predictions

        df.to_csv(
            output_path,
            index=False,
        )


        logging.info(
            f"Prediction output saved at {output_path}"
        )


        # Convert DataFrame into HTML table

        table_html = df.to_html(
            classes="prediction-table",
            index=False,
        )


        # Render prediction result page

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={
                "table": table_html,

                "total_records":
                    total_records,

                "legitimate_count":
                    legitimate_count,

                "phishing_count":
                    phishing_count,

                "legitimate_percentage":
                    legitimate_percentage,

                "phishing_percentage":
                    phishing_percentage,
            },
        )


    except Exception as e:

        logging.exception(
            "Prediction failed."
        )

        raise NetworkSecurityException(
            e,
            sys,
        )


if __name__ == "__main__":

    app_run(
        app,
        host="0.0.0.0",
        port=8000,
    )