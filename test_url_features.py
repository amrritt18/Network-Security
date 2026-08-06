from networksecurity.utils.url_utils.url_feature_extractor import (
    URLFeatureExtractor,
)

from networksecurity.utils.main_utils.utils import (
    load_object,
)


# ---------------------------------------------------------
# ENTER URL
# ---------------------------------------------------------

url = input(
    "Enter website URL: "
)


print(
    "\nExtracting URL features..."
)


# ---------------------------------------------------------
# EXTRACT 30 FEATURES
# ---------------------------------------------------------

extractor = URLFeatureExtractor(
    url
)

df = extractor.get_dataframe()


print(
    f"\nFeatures extracted successfully: {df.shape[1]}"
)


# ---------------------------------------------------------
# LOAD FINAL MODEL
# ---------------------------------------------------------

model = load_object(
    file_path="final_model/model.pkl"
)


print(
    "\nModel loaded successfully."
)


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

prediction = model.predict(
    df
)


print(
    "\nRaw prediction:",
    prediction
)


print(
    "\nRaw prediction value:",
    prediction[0]
)