import os
import sys
import socket
import ipaddress
from urllib.parse import urlparse

import certifi
import pandas as pd
import pymongo

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Request,
    Form,
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

from networksecurity.utils.url_utils.url_feature_extractor import (
    URLFeatureExtractor,
)

from networksecurity.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

MONGO_DB_URL = os.getenv(
    "MONGO_DB_URL"
)

if not MONGO_DB_URL:
    raise ValueError(
        "MONGO_DB_URL is not found in the .env file."
    )


# ============================================================
# MONGODB CONNECTION
# ============================================================

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


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Network Security API",
    description=(
        "Machine Learning Based "
        "Phishing Website Detection API"
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="./templates"
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    "final_model",
    "model.pkl",
)


# ============================================================
# LABEL MAPPING
#
# Original dataset:
#
#  1  -> Legitimate
# -1  -> Phishing
#
# Data transformation:
#
# -1 -> 0
#
# Therefore:
#
#  1 -> Legitimate
#  0 -> Phishing
# ============================================================

PREDICTION_LABELS = {
    0: "Phishing",
    1: "Legitimate",
    0.0: "Phishing",
    1.0: "Legitimate",
}


# ============================================================
# LOAD MODEL
# ============================================================

def get_model():

    if not os.path.exists(
        MODEL_PATH
    ):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}"
        )

    model = load_object(
        file_path=MODEL_PATH
    )

    return model


# ============================================================
# URL SECURITY CHECK
# ============================================================

def validate_public_url(
    url: str,
) -> str:
    """
    Validate a user supplied URL before the feature extractor
    makes network requests.

    Blocks localhost, private IP addresses, loopback addresses,
    link-local addresses and other non-public targets.
    """

    url = url.strip()

    if not url:
        raise ValueError(
            "Please enter a website URL."
        )

    if not url.lower().startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    parsed = urlparse(
        url
    )

    if parsed.scheme not in (
        "http",
        "https",
    ):
        raise ValueError(
            "Only HTTP and HTTPS URLs are allowed."
        )

    hostname = parsed.hostname

    if not hostname:
        raise ValueError(
            "Invalid website URL."
        )

    hostname_lower = (
        hostname.lower()
    )

    if hostname_lower in (
        "localhost",
        "localhost.localdomain",
    ):
        raise ValueError(
            "Localhost URLs are not allowed."
        )

    try:

        address_info = (
            socket.getaddrinfo(
                hostname,
                None,
            )
        )

        addresses = {
            item[4][0]
            for item in address_info
        }

        for address in addresses:

            ip = ipaddress.ip_address(
                address
            )

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):

                raise ValueError(
                    "Private or local network "
                    "URLs are not allowed."
                )

    except socket.gaierror:

        raise ValueError(
            "The website domain could not be resolved."
        )

    return url


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
async def index(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# ============================================================
# TRAIN MODEL
# ============================================================

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

            "message":
                "Training completed successfully",

            "model_path":
                model_trainer_artifact
                .trained_model_file_path,
        }

    except Exception as e:

        logging.exception(
            "Training failed."
        )

        raise NetworkSecurityException(
            e,
            sys,
        )


# ============================================================
# CSV PREDICTION
# ============================================================

@app.post("/predict")
async def predict_route(
    request: Request,
    file: UploadFile = File(...),
):

    try:

        logging.info(
            "CSV prediction request received."
        )

        # ----------------------------------------------------
        # Validate CSV
        # ----------------------------------------------------

        if not file.filename.lower().endswith(
            ".csv"
        ):

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error":
                        "Please upload a valid CSV file."
                },
            )

        # ----------------------------------------------------
        # Read CSV
        # ----------------------------------------------------

        df = pd.read_csv(
            file.file
        )

        if df.empty:

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error":
                        "Uploaded CSV file is empty."
                },
            )

        logging.info(
            f"Prediction dataset shape: {df.shape}"
        )

        # ----------------------------------------------------
        # Load Model
        # ----------------------------------------------------

        network_model = get_model()

        logging.info(
            "Model loaded successfully."
        )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        y_pred = (
            network_model.predict(
                df
            )
        )

        # ----------------------------------------------------
        # Convert prediction to labels
        # ----------------------------------------------------

        df[
            "Prediction_Code"
        ] = y_pred

        df[
            "Prediction"
        ] = (
            df[
                "Prediction_Code"
            ].map(
                PREDICTION_LABELS
            )
        )

        df.drop(
            columns=[
                "Prediction_Code"
            ],
            inplace=True,
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        total_records = len(
            df
        )

        legitimate_count = int(
            (
                df["Prediction"]
                == "Legitimate"
            ).sum()
        )

        phishing_count = int(
            (
                df["Prediction"]
                == "Phishing"
            ).sum()
        )

        legitimate_percentage = round(
            (
                legitimate_count
                / total_records
            )
            * 100,
            2,
        )

        phishing_percentage = round(
            (
                phishing_count
                / total_records
            )
            * 100,
            2,
        )

        # ----------------------------------------------------
        # Save Output
        # ----------------------------------------------------

        os.makedirs(
            "prediction_output",
            exist_ok=True,
        )

        output_path = os.path.join(
            "prediction_output",
            "output.csv",
        )

        df.to_csv(
            output_path,
            index=False,
        )

        logging.info(
            f"Prediction output saved: {output_path}"
        )

        # ----------------------------------------------------
        # HTML Table
        # ----------------------------------------------------

        table_html = df.to_html(
            classes="prediction-table",
            index=False,
        )

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={

                "table":
                    table_html,

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
            "CSV prediction failed."
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error":
                    f"Prediction failed: {str(e)}"
            },
        )


# ============================================================
# URL PREDICTION
# ============================================================

@app.post("/predict-url")
async def predict_url_route(
    request: Request,
    url: str = Form(...),
):

    try:

        logging.info(
            f"URL prediction request received: {url}"
        )

        # ----------------------------------------------------
        # Validate URL before fetching it
        # ----------------------------------------------------

        safe_url = validate_public_url(
            url
        )

        logging.info(
            "URL security validation successful."
        )

        # ----------------------------------------------------
        # Extract 30 Features
        # ----------------------------------------------------

        extractor = URLFeatureExtractor(
            safe_url
        )

        feature_df = (
            extractor.get_dataframe()
        )

        logging.info(
            "URL features extracted successfully."
        )

        logging.info(
            f"Number of URL features: "
            f"{feature_df.shape[1]}"
        )

        # ----------------------------------------------------
        # Safety Check
        # ----------------------------------------------------

        if feature_df.shape[1] != 30:

            raise ValueError(
                "URL feature extraction did not "
                "produce exactly 30 features."
            )

        # ----------------------------------------------------
        # Load Model
        # ----------------------------------------------------

        network_model = get_model()

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = (
            network_model.predict(
                feature_df
            )
        )

        prediction_code = int(
            prediction[0]
        )

        prediction_label = (
            PREDICTION_LABELS.get(
                prediction_code,
                "Unknown",
            )
        )

        logging.info(
            f"URL Prediction Code: "
            f"{prediction_code}"
        )

        logging.info(
            f"URL Prediction: "
            f"{prediction_label}"
        )

        # ----------------------------------------------------
        # Return Result
        # ----------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={

                "url":
                    safe_url,

                "url_prediction":
                    prediction_label,

                "prediction_code":
                    prediction_code,
            },
        )

    except ValueError as e:

        logging.warning(
            f"Invalid URL request: {e}"
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "url_error":
                    str(e)
            },
        )

    except Exception as e:

        logging.exception(
            "URL prediction failed."
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "url_error":
                    f"Unable to analyze website: {str(e)}"
            },
        )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app_run(
        app,
        host="0.0.0.0",
        port=8000,
    )