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

st.title("Test my model remotely!")
st.write(
    "Input the required data, start execution and give feedback!"
)

# Define parameters
parameters = [
    'Dedicated team members', 'Team size', 'Object points',
    'Actual duration', 'Estimated duration', 'Degree of risk management',
    'Economic instability impact', 'Development environment adequacy',
    'Estimated size', 'Other sizing method', 'Comments within the code',
    'Application domain', 'Income satisfaction',
    'Top management opinion of previous system', 'Requirment stability'
]

st.title("Project Parameters Input")

# Create input fields for each parameter
inputs = {}
for param in parameters:
    inputs[param] = st.number_input(f"{param}", min_value=0, step=1, format="%d")

# Display collected inputs
st.write("### Entered Values:")
st.json(inputs)