# 🛡️ Network Security Detection System

## Machine Learning Based Phishing Website Detection

An end-to-end Machine Learning application for detecting **phishing websites** using website and URL-related security characteristics.

The project implements a complete Machine Learning workflow including:

- Data Ingestion
- Data Validation
- Data Drift Detection
- Data Transformation
- Model Training
- Hyperparameter Tuning
- Model Evaluation
- Model Serialization
- MongoDB Integration
- FastAPI Model Serving
- CSV-Based Batch Prediction
- Direct Website URL Prediction
- Web-Based User Interface

The application supports two prediction modes:

1. **CSV Prediction** — Upload a dataset containing the required website security features.
2. **URL Prediction** — Enter a website URL and automatically extract 30 phishing-related features before performing prediction.

---

# 📌 Project Overview

Phishing websites are malicious websites designed to imitate legitimate services and trick users into providing sensitive information such as:

- Usernames
- Passwords
- Banking information
- Personal information
- Login credentials

This project uses Machine Learning to analyze website characteristics and classify websites as:

```text
Legitimate
or
Phishing
```

The system is designed using a modular Machine Learning architecture rather than keeping the complete workflow inside a single notebook.

---

# 🎯 Project Objectives

The major objectives of this project are:

- Build an end-to-end Machine Learning pipeline
- Detect phishing websites using security-related features
- Automate data ingestion and preprocessing
- Validate incoming datasets before model training
- Detect data drift between training and testing datasets
- Train and compare multiple classification algorithms
- Perform hyperparameter tuning
- Automatically select the best-performing model
- Save the trained model and preprocessing pipeline
- Build a prediction API using FastAPI
- Support CSV-based batch prediction
- Support direct website URL prediction
- Automatically extract URL and webpage security features
- Provide a simple browser-based prediction interface
- Maintain a modular and scalable project structure

---

# ✨ Key Features

## 📥 Data Ingestion

The Data Ingestion component retrieves the source dataset and prepares the data for the Machine Learning pipeline.

Responsibilities include:

- Connecting to the data source
- Loading the phishing dataset
- Converting records into Pandas DataFrames
- Splitting data into training and testing datasets
- Saving generated datasets as pipeline artifacts

MongoDB is used as part of the project's data ingestion infrastructure.

---

# ✅ Data Validation

Before training, the dataset passes through a dedicated validation stage.

The validation pipeline checks:

- Dataset structure
- Required columns
- Target column
- Data types
- Missing values
- Duplicate records
- Numerical columns
- Train/test compatibility

This prevents invalid or unexpected data from silently entering the training pipeline.

---

# 📊 Data Drift Detection

The project performs statistical data drift detection using the:

**Kolmogorov-Smirnov (KS) Two-Sample Test**

The distributions of training and testing features are compared to identify significant differences.

A drift report can contain information such as:

```yaml
URL_Length:
  drift_status: false
  ks_statistic: 0.001696
  p_value: 1.0
  threshold: 0.05
```

The generated drift report is stored as a YAML artifact.

---

# 🔄 Data Transformation

The transformation pipeline prepares validated data for Machine Learning.

The project uses:

```text
KNNImputer
```

inside a Scikit-Learn preprocessing pipeline.

The transformation stage:

- Separates input features and target
- Handles missing values
- Fits preprocessing only on training data
- Transforms training data
- Transforms testing data
- Converts target labels for binary classification
- Saves transformed NumPy arrays
- Saves the fitted preprocessing object

## Target Transformation

The original dataset contains:

```text
Result = 1
Result = -1
```

For model training:

```text
-1 → 0
 1 → 1
```

Therefore, the final model classes are interpreted as:

```text
0 → Phishing
1 → Legitimate
```

---

# 🤖 Machine Learning Models

Multiple classification algorithms are evaluated during training.

The project includes:

- Random Forest Classifier
- Decision Tree Classifier
- Gradient Boosting Classifier
- Logistic Regression
- AdaBoost Classifier

Hyperparameter tuning is performed using:

```text
GridSearchCV
```

The pipeline evaluates candidate models and automatically selects the best-performing model.

---

# 📈 Model Evaluation

The trained models are evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score

A successful training run produced approximately:

| Metric | Training | Testing |
|---|---:|---:|
| Accuracy | 99.05% | 96.97% |
| Precision | 98.77% | 96.24% |
| Recall | 99.53% | 98.36% |
| F1 Score | 99.15% | 97.29% |

These metrics correspond to evaluation on the prepared dataset/test pipeline.

> **Important:** These test metrics should not automatically be interpreted as the accuracy of the experimental live-URL prediction mode. Live URL prediction generates features dynamically, and some reputation-oriented features require approximations or external information.

---

# 🧠 Final Prediction Model

The final prediction object combines the preprocessing pipeline and trained classifier:

```text
Raw Features
      ↓
Preprocessing Pipeline
      ↓
Trained Classification Model
      ↓
Prediction
```

The custom:

```text
NetworkModel
```

provides a single prediction interface.

Conceptually:

```python
prediction = network_model.predict(data)
```

internally performs:

```text
Raw Input
    ↓
Preprocessor
    ↓
Transformed Features
    ↓
Trained Model
    ↓
Prediction
```

This helps maintain consistency between training and inference.

---

# 🌐 Prediction Modes

The application currently supports two prediction methods.

## 1️⃣ CSV-Based Batch Prediction

Users can upload a CSV file containing the required 30 website features.

Workflow:

```text
CSV File
    ↓
FastAPI
    ↓
Pandas DataFrame
    ↓
NetworkModel
    ↓
Preprocessing
    ↓
ML Classifier
    ↓
Predictions
    ↓
Legitimate / Phishing
    ↓
Prediction Summary
```

The result page displays:

- Total analyzed records
- Number of legitimate predictions
- Number of phishing predictions
- Legitimate percentage
- Phishing percentage
- Detailed prediction table

The prediction output is also saved as:

```text
prediction_output/output.csv
```

---

# 🔗 Direct Website URL Prediction

The application also includes an experimental direct URL prediction mode.

Instead of manually creating a CSV file, the user can enter:

```text
https://www.example.com
```

The system automatically extracts the required features and sends them to the trained model.

Workflow:

```text
Website URL
      ↓
URL Validation
      ↓
URL Feature Extractor
      ↓
30 Security Features
      ↓
NetworkModel
      ↓
Preprocessing
      ↓
ML Classifier
      ↓
Prediction
      ↓
Legitimate / Phishing
```

This allows the application to provide a much simpler user experience.

---

# 🔍 URL Feature Extraction

The custom URL feature extractor analyzes multiple characteristics of the submitted website.

The 30 model features are:

```text
1.  having_IP_Address
2.  URL_Length
3.  Shortining_Service
4.  having_At_Symbol
5.  double_slash_redirecting
6.  Prefix_Suffix
7.  having_Sub_Domain
8.  SSLfinal_State
9.  Domain_registeration_length
10. Favicon
11. port
12. HTTPS_token
13. Request_URL
14. URL_of_Anchor
15. Links_in_tags
16. SFH
17. Submitting_to_email
18. Abnormal_URL
19. Redirect
20. on_mouseover
21. RightClick
22. popUpWidnow
23. Iframe
24. age_of_domain
25. DNSRecord
26. web_traffic
27. Page_Rank
28. Google_Index
29. Links_pointing_to_page
30. Statistical_report
```

Feature extraction uses information from:

- URL structure
- Domain information
- DNS resolution
- SSL/TLS information
- WHOIS information
- HTML content
- Links and resources
- Forms
- JavaScript-related patterns
- Redirect behavior

---

# ⚠️ Live URL Prediction Limitation

The original phishing dataset contains several features that historically depend on external reputation, ranking, indexing, or backlink information.

Examples include:

```text
web_traffic
Page_Rank
Google_Index
Links_pointing_to_page
Statistical_report
```

Some of these values cannot be reproduced exactly today using only a submitted URL.

Therefore, the current URL feature extractor uses practical live approximations for some features.

As a result:

> **The URL prediction functionality should currently be considered an experimental/demo feature until it is separately validated on a labeled live-URL dataset.**

The CSV-based model evaluation remains the validated prediction workflow for the reported test metrics.

---

# 🔐 URL Security Validation

Because direct URL prediction requires the backend to retrieve information from a submitted URL, the FastAPI application performs URL validation before feature extraction.

The application rejects targets such as:

```text
localhost
127.0.0.1
private network addresses
loopback addresses
link-local addresses
reserved addresses
```

Only HTTP and HTTPS URLs are accepted.

This provides basic protection against Server-Side Request Forgery (SSRF) attempts.

---

# 🌐 FastAPI Web Application

The trained model is integrated into a FastAPI application.

The browser interface provides two options:

```text
┌─────────────────────────────────────┐
│ Network Security Detection System   │
│                                     │
│       Check Website URL             │
│                                     │
│ [ https://www.example.com        ]  │
│                                     │
│        [ Check Website ]            │
│                                     │
│                OR                   │
│                                     │
│         Upload Dataset              │
│                                     │
│          [ Choose File ]            │
│                                     │
│        [ Analyze Dataset ]          │
└─────────────────────────────────────┘
```

URL predictions are displayed directly on the home page.

Example:

```text
✓ Legitimate Website
```

or:

```text
⚠ Phishing Website Detected
```

CSV predictions are displayed on a separate result page containing prediction statistics and the detailed table.

---

# 🔌 API Endpoints

## Home

```http
GET /
```

Displays the main prediction interface.

---

## CSV Prediction

```http
POST /predict
```

Accepts a CSV file containing website features and performs batch phishing prediction.

---

## URL Prediction

```http
POST /predict-url
```

Accepts a website URL.

The endpoint:

```text
Validates URL
      ↓
Extracts 30 Features
      ↓
Loads NetworkModel
      ↓
Performs Prediction
      ↓
Returns Legitimate / Phishing
```

---

## Training

```http
GET /train
```

Triggers the complete training pipeline.

> This endpoint is primarily intended for development/testing. Authentication or another protection mechanism should be added before exposing model training in a production environment.

---

## Swagger Documentation

FastAPI automatically generates interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 📁 Project Structure

```text
NETWORK_SECURITY/
│
├── app.py
├── main.py
├── push_data.py
├── README.md
├── requirements.txt
├── setup.py
├── .env
├── .gitignore
│
├── data_schema/
│   └── schema.yaml
│
├── Network_Data/
│   └── phisingData.csv
│
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
│
├── prediction_output/
│   └── output.csv
│
├── templates/
│   ├── index.html
│   └── table.html
│
├── networksecurity/
│   │
│   ├── __init__.py
│   │
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   │
│   ├── constants/
│   │   └── training_pipeline/
│   │
│   ├── entity/
│   │   ├── artifact_entity.py
│   │   └── config_entity.py
│   │
│   ├── exception/
│   │   └── exception.py
│   │
│   ├── logging/
│   │   └── logger.py
│   │
│   ├── pipeline/
│   │   ├── batch_pipeline.py
│   │   └── training_pipeline.py
│   │
│   ├── utils/
│   │   ├── main_utils/
│   │   ├── ml_utils/
│   │   └── url_utils/
│   │       └── url_feature_extractor.py
│   │
│   └── cloud/
│       └── s3_syncer.py
│
├── valid_data/
│   └── test.csv
│
└── logs/
```

---

# 🛠️ Technologies Used

## Programming

- Python

## Data Processing

- NumPy
- Pandas

## Machine Learning

- Scikit-Learn
- SciPy

## Database

- MongoDB
- PyMongo

## Backend

- FastAPI
- Uvicorn

## Frontend

- HTML
- CSS
- Jinja2

## URL & Web Analysis

- Requests
- BeautifulSoup
- python-whois
- Socket
- SSL
- DNS resolution

## Configuration

- YAML
- python-dotenv

## Development Tools

- Git
- GitHub
- VS Code
- Python Virtual Environment

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd NETWORK_SECURITY
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For URL prediction, make sure the required packages are installed:

```bash
pip install requests beautifulsoup4 python-whois python-multipart
```

---

# 🔐 Environment Variables

Create:

```text
.env
```

inside the project root.

Example:

```env
MONGO_DB_URL=your_mongodb_connection_string
```

Never commit credentials to GitHub.

Your `.gitignore` should include:

```gitignore
.env
.venv/
__pycache__/
*.pyc
logs/
```

---

# ▶️ Running the Application

Start FastAPI using:

```bash
uvicorn app:app --reload
```

The application normally runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 URL Prediction Example

Start the application:

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Enter a URL such as:

```text
https://www.google.com
```

Click:

```text
Check Website
```

The system performs:

```text
URL
 ↓
Security Validation
 ↓
30 Feature Extraction
 ↓
Model Prediction
 ↓
Result
```

Example output:

```text
✓ Legitimate Website
```

---

# 📂 CSV Prediction Example

Open the application and choose:

```text
Upload Dataset
```

Select a CSV file containing the required input features.

Click:

```text
Analyze Dataset
```

The application displays:

```text
Total Records
Legitimate Records
Phishing Records
Legitimate Percentage
Phishing Percentage
Detailed Prediction Table
```

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │     Source Data      │
                         │      MongoDB         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Data Ingestion     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Data Validation    │
                         │ + Drift Detection    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Data Transformation  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Model Training    │
                         │ + Model Selection    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     NetworkModel     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         └──────────┬───────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
             ┌──────────────────┐       ┌──────────────────┐
             │    CSV Upload    │       │   Website URL    │
             │    Prediction    │       │    Prediction    │
             └────────┬─────────┘       └────────┬─────────┘
                      │                           │
                      │                  ┌────────▼─────────┐
                      │                  │ Feature Extractor│
                      │                  │   30 Features    │
                      │                  └────────┬─────────┘
                      │                           │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Legitimate/Phishing  │
                         └──────────────────────┘
```

---

# 🔒 Security Considerations

Sensitive credentials are managed using environment variables rather than hard-coded values.

Files such as:

```text
.env
.venv/
__pycache__/
logs/
```

should not be committed to a public repository.

Credentials such as:

- MongoDB passwords
- Cloud credentials
- API tokens
- Access keys

must never be stored directly in source code.

The URL prediction endpoint also performs basic validation to prevent requests to private/local network resources.

---

# 🚀 Future Improvements

The project can be extended with:

- More accurate real-time URL feature extraction
- External domain reputation APIs
- Phishing blacklist integration
- URL-mode validation on a labeled live dataset
- Probability/confidence score
- Docker containerization
- CI/CD pipeline
- Cloud deployment
- AWS S3 artifact storage
- MLflow experiment tracking
- DagsHub integration
- Model registry
- Automated retraining
- Production monitoring
- Prediction logging
- Advanced drift monitoring
- Model versioning
- Authentication for training endpoints
- Improved frontend dashboard

---

# 📈 Current Project Status

| Component | Status |
|---|---|
| Data Ingestion | ✅ Completed |
| MongoDB Integration | ✅ Completed |
| Data Validation | ✅ Completed |
| Schema Validation | ✅ Completed |
| Data Drift Detection | ✅ Completed |
| Data Transformation | ✅ Completed |
| Model Training | ✅ Completed |
| Hyperparameter Tuning | ✅ Completed |
| Model Evaluation | ✅ Completed |
| Model Serialization | ✅ Completed |
| FastAPI Backend | ✅ Completed |
| CSV Prediction | ✅ Completed |
| CSV Prediction Dashboard | ✅ Completed |
| Web Interface | ✅ Completed |
| URL Feature Extractor | ✅ Implemented |
| Direct URL Prediction | 🧪 Experimental |
| URL Security Validation | ✅ Implemented |
| Docker | 🔜 Future Enhancement |
| Cloud Deployment | 🔜 Future Enhancement |
| CI/CD | 🔜 Future Enhancement |
| Live URL Accuracy Validation | 🔜 Future Enhancement |

---

# 🎓 Learning Outcomes

This project demonstrates practical understanding of:

- End-to-end Machine Learning development
- Modular Python architecture
- Classification algorithms
- Hyperparameter optimization
- Data preprocessing
- KNN imputation
- Statistical data drift detection
- Model evaluation
- Model serialization
- MongoDB integration
- FastAPI development
- REST API concepts
- HTML and Jinja2 integration
- URL feature engineering
- HTML parsing
- WHOIS lookup
- DNS and SSL analysis
- Environment variable management
- Basic API security
- ML model serving
- MLOps-oriented project architecture

---

# 👨‍💻 Author

**Amrit Raj**

M.Tech — Robotics & Artificial Intelligence  
Indian Institute of Technology Bhubaneswar

### Areas of Interest

- Machine Learning
- Artificial Intelligence
- Robotics
- Computer Vision
- Generative AI
- MLOps

---

# 📄 License

This project is developed for educational, research, demonstration, and portfolio purposes.

---

# ⭐ Project Summary

The **Network Security Detection System** demonstrates how a Machine Learning model can be developed beyond a notebook and converted into a modular, end-to-end application.

The project combines:

```text
Data Engineering
      +
Data Validation
      +
Data Drift Detection
      +
Machine Learning
      +
Hyperparameter Tuning
      +
MongoDB
      +
FastAPI
      +
URL Feature Engineering
      +
Web-Based Model Serving
```

to build a complete phishing website detection system.

The validated ML pipeline supports batch prediction from structured CSV data, while the project additionally explores **direct website URL analysis** through automatic extraction of 30 phishing-related security features.