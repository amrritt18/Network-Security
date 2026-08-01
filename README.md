# 🛡️ Network Security Detection System

## Machine Learning Based Phishing Website Detection

An end-to-end Machine Learning application for detecting **phishing websites** from website and URL-related security features.

The project implements a complete ML workflow including **data ingestion, data validation, data drift detection, data transformation, model training, model evaluation, prediction, and web-based deployment using FastAPI**.

The trained model is integrated with a simple web interface where users can upload a CSV dataset and receive phishing detection results.

---

## 📌 Project Overview

Phishing websites are designed to imitate legitimate websites in order to steal sensitive information such as usernames, passwords, banking information, and other credentials.

This project uses Machine Learning to analyze characteristics of websites and classify them based on their phishing-related behavior.

The complete workflow is:

```text
Dataset / MongoDB
        ↓
Data Ingestion
        ↓
Data Validation
        ↓
Data Drift Detection
        ↓
Data Transformation
        ↓
Model Training
        ↓
Model Evaluation
        ↓
Best Model Selection
        ↓
Model Serialization
        ↓
FastAPI Application
        ↓
CSV Upload
        ↓
Phishing Prediction
        ↓
Web-Based Results
```

---

## 🎯 Project Objectives

The major objectives of this project are:

- Build an end-to-end Machine Learning pipeline
- Detect phishing websites using website security features
- Automate data ingestion and preprocessing
- Validate incoming datasets before model training
- Detect data drift between training and testing datasets
- Train and compare multiple classification algorithms
- Automatically select the best-performing model
- Save the preprocessing pipeline and trained model
- Build a prediction API using FastAPI
- Provide a user-friendly web interface for predictions
- Maintain a modular and scalable project structure

---

## ✨ Key Features

### Data Ingestion

The Data Ingestion component retrieves the dataset and prepares training and testing datasets.

Responsibilities include:

- Loading source data
- Converting data into Pandas DataFrames
- Creating training and testing datasets
- Saving generated datasets as pipeline artifacts

---

### Data Validation

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

This prevents invalid data from silently entering the training pipeline.

---

### Data Drift Detection

The project performs statistical data drift detection using the:

**Kolmogorov-Smirnov (KS) Two-Sample Test**

For every feature, the distributions of training and testing data are compared.

A drift report is generated containing information such as:

```yaml
URL_Length:
  drift_status: false
  ks_statistic: 0.001696
  p_value: 1.0
  threshold: 0.05
```

The drift report is stored as a YAML artifact.

---

## 🔄 Data Transformation

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
- Converts the target labels for classification
- Saves transformed arrays
- Saves the fitted preprocessing object

The transformed datasets are stored as NumPy arrays.

---

## 🤖 Machine Learning Models

Multiple classification algorithms are evaluated during model training.

The current project includes:

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

## 📊 Model Evaluation

The model is evaluated using multiple classification metrics:

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

These results indicate strong classification performance while maintaining good generalization on the test dataset.

---

## 🧠 Final Prediction Model

The final prediction object combines:

```text
Preprocessing Pipeline
        +
Trained Classification Model
        ↓
NetworkModel
```

The custom `NetworkModel` performs preprocessing and prediction through a single interface.

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
Transformed Input
    ↓
Trained Model
    ↓
Prediction
```

This helps keep training and inference preprocessing consistent.

---

## 🌐 FastAPI Web Application

The trained model is integrated into a FastAPI application.

The application provides a browser-based interface where a user can:

1. Open the application
2. Upload a CSV file
3. Submit the dataset for analysis
4. Run predictions using the trained model
5. View the prediction summary
6. Inspect individual prediction results

The result page displays:

- Total number of analyzed records
- Number of legitimate predictions
- Number of phishing predictions
- Prediction percentages
- Detailed prediction table

---

## 🔌 API Endpoints

### Home

```http
GET /
```

Displays the web interface for uploading prediction data.

### Prediction

```http
POST /predict
```

Accepts a CSV file and performs phishing website prediction.

### Training

```http
GET /train
```

Triggers the training pipeline.

> The training endpoint is intended primarily for development/testing and should be protected or redesigned before exposing it in a production environment.

### API Documentation

FastAPI automatically provides Swagger documentation at:

```text
/docs
```

---

## 📁 Project Structure

```text
NETWORK_SECURITY/
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── table.html
│
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
│
├── prediction_output/
│   └── output.csv
│
├── artifacts/
│
└── networksecurity/
    │
    ├── __init__.py
    │
    ├── components/
    │   ├── data_ingestion.py
    │   ├── data_validation.py
    │   ├── data_transformation.py
    │   └── model_trainer.py
    │
    ├── constants/
    │   └── training_pipeline.py
    │
    ├── entity/
    │   ├── artifact_entity.py
    │   └── config_entity.py
    │
    ├── exception/
    │   └── exception.py
    │
    ├── logging/
    │   └── logger.py
    │
    ├── pipeline/
    │   └── training_pipeline.py
    │
    ├── utils/
    │   ├── main_utils/
    │   └── ml_utils/
    │
    └── cloud/
```

---

## 🛠️ Technologies Used

### Programming

- Python

### Data Processing

- NumPy
- Pandas

### Machine Learning

- Scikit-Learn
- SciPy

### Database

- MongoDB
- PyMongo

### Backend

- FastAPI
- Uvicorn

### Frontend

- HTML
- CSS
- Jinja2 Templates

### Model Serialization

- Pickle

### Configuration

- YAML
- python-dotenv

### Development Tools

- Git
- GitHub
- VS Code
- Python Virtual Environment

---

## 📋 Dataset Features

The model analyzes multiple website and URL-related security characteristics, including:

```text
having_IP_Address
URL_Length
Shortining_Service
having_At_Symbol
double_slash_redirecting
Prefix_Suffix
having_Sub_Domain
SSLfinal_State
Domain_registeration_length
Favicon
port
HTTPS_token
Request_URL
URL_of_Anchor
Links_in_tags
SFH
Submitting_to_email
Abnormal_URL
Redirect
on_mouseover
RightClick
popUpWidnow
Iframe
age_of_domain
DNSRecord
web_traffic
Page_Rank
Google_Index
Links_pointing_to_page
Statistical_report
```

The target variable used during training is:

```text
Result
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd NETWORK_SECURITY
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
MONGO_DB_URL=your_mongodb_connection_string
```

Never commit the `.env` file to a public repository.

Add it to `.gitignore`:

```gitignore
.env
```

---

## ▶️ Running the Application

Start the FastAPI application using:

```bash
uvicorn app:app --reload
```

The application will normally run at:

```text
http://127.0.0.1:8000
```

Open the address in your browser to access the prediction interface.

Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 🔍 Prediction Workflow

The prediction workflow is:

```text
User Uploads CSV
       ↓
FastAPI receives file
       ↓
Pandas reads CSV
       ↓
Saved NetworkModel loaded
       ↓
Preprocessor transforms features
       ↓
ML classifier generates predictions
       ↓
Predictions converted to readable labels
       ↓
Prediction summary calculated
       ↓
Results saved
       ↓
HTML result page displayed
```

---

## 🧪 Example Usage

1. Start the FastAPI server.

```bash
uvicorn app:app --reload
```

2. Open the application in the browser.

3. Select a CSV file containing the required input features.

4. Click:

```text
Analyze Dataset
```

5. The system processes the uploaded records and displays the prediction results.

---

## 🏗️ MLOps-Oriented Architecture

The project was designed using a modular pipeline architecture rather than keeping all Machine Learning logic inside a single notebook.

```text
                    ┌──────────────────────┐
                    │     Source Data      │
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
                    │    Model Trainer     │
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
                               ▼
                    ┌──────────────────────┐
                    │  Prediction Website  │
                    └──────────────────────┘
```

---

## 🔒 Security Considerations

Sensitive credentials are managed through environment variables rather than being hard-coded into application source code.

Files such as the following should not be committed:

```text
.env
.venv/
__pycache__/
logs/
prediction_output/
```

Credentials such as MongoDB passwords, cloud access keys, and API tokens must never be stored directly in the source code.

---

## 🚀 Future Improvements

The current project can be extended with:

- Docker containerization
- CI/CD pipeline
- Cloud deployment
- AWS S3 model and artifact storage
- MLflow experiment tracking
- DagsHub integration
- Model registry
- Automated model retraining
- Production monitoring
- Advanced data drift monitoring
- Prediction logging
- Model versioning
- Authentication for training endpoints
- Improved frontend dashboard
- Real-time single-URL phishing prediction

These features can be integrated incrementally without changing the core Machine Learning architecture.

---

## 📈 Current Project Status

| Component | Status |
|---|---|
| Data Ingestion | ✅ Completed |
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
| Web Interface | ✅ Completed |
| MongoDB Integration | ✅ Completed |
| Docker | 🔜 Future Enhancement |
| Cloud Deployment | 🔜 Future Enhancement |
| CI/CD | 🔜 Future Enhancement |

---

## 🎓 Learning Outcomes

This project demonstrates practical understanding of:

- End-to-end Machine Learning project development
- Modular Python project architecture
- Classification algorithms
- Hyperparameter optimization
- Data preprocessing pipelines
- Statistical data drift detection
- Model evaluation
- Model serialization
- MongoDB integration
- FastAPI development
- REST API concepts
- HTML/Jinja2 integration
- Environment variable management
- ML model serving

---

## 👨‍💻 Author

**Amrit Raj**

M.Tech — Robotics & Artificial Intelligence  
Indian Institute of Technology Bhubaneswar

Areas of Interest:

- Machine Learning
- Artificial Intelligence
- Robotics
- Computer Vision
- MLOps

---

## 📄 License

This project is developed for educational, research, and portfolio purposes.

---

## ⭐ Project Summary

The **Network Security Detection System** demonstrates how a Machine Learning model can be developed beyond a notebook and organized into a complete application.

It combines:

**Data Engineering + Data Validation + Machine Learning + MLOps Architecture + API Development + Web-Based Model Serving**

to provide an end-to-end phishing website detection system.