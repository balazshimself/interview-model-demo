import json
import streamlit as st
from google.cloud import firestore

# Load Firestore credentials from Streamlit secrets
firestore_credentials = json.loads(st.secrets["gcp_service_account"])
db = firestore.Client.from_service_account_info(firestore_credentials)

# Function to log predictions
def log_prediction(inputs, prediction):
    log_data = {
        "features": inputs,
        "prediction": prediction,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("logs").add(log_data)  # Store in Firestore

st.title("My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)