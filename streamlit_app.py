import json
import streamlit as st
from google.cloud import firestore
import pandas as pd
import random

# Load Firestore credentials from Streamlit secrets
firestore_credentials = st.secrets["gcp_service_account"]
db = firestore.Client.from_service_account_info(firestore_credentials)
df = pd.read_excel('SEERA_dataset.xlsx')

# Define parameters
int_parameters = [
    'Dedicated team members', 'Team size', 'Object points', 'Degree of risk management',
    'Economic instability impact', 'Development environment adequacy',
    'Estimated size', 'Other sizing method', 'Comments within the code',
    'Application domain', 'Income satisfaction'
]

float_parameters_by_half = [
    'Actual duration', 'Estimated duration'
]

float_parameters_by_hundredth = [
    'Requirement stability'
]

bool_parameters = [
    'Top management opinion of previous system'
]
expected_keys = int_parameters + float_parameters_by_half + float_parameters_by_hundredth + bool_parameters

# Function to log predictions
def log_prediction(inputs, prediction):
    log_data = {
        "features": inputs,
        "prediction": prediction,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("logs").add(log_data)  # Store in Firestore

# Dummy prediction function – replace with your model's prediction code.
def predict_cost(features):
    # For demonstration, simply sum all numeric values
    total = 0
    for v in features.values():
        if isinstance(v, bool):
            total += 1 if v else 0
        else:
            total += float(v)
    return total

# Function to load a random row from an Excel file
def use_actual_data():
    # Make sure the Excel file is accessible by your app (adjust the path as needed)
    row_dict = df.sample(n=1).to_dict(orient='records')[0]

    filtered_data = {key: value for key, value in row_dict.items() if key in expected_keys}
    return filtered_data

def update_inputs_from_actual_data(inputs, actual_data):
    for key in expected_keys:
        if key in actual_data:
            value = actual_data[key]
            if pd.notnull(value):
                if key in int_parameters:
                    try:
                        new_val = int(value)
                    except (ValueError, TypeError):
                        continue
                elif key in float_parameters_by_half or key in float_parameters_by_hundredth:
                    try:
                        new_val = float(value)
                    except (ValueError, TypeError):
                        continue
                elif key in bool_parameters:
                    if isinstance(value, bool):
                        new_val = value
                    elif isinstance(value, str):
                        new_val = value.strip().lower() in ['true', '1', 'yes']
                    else:
                        new_val = bool(value)
                # Update the inputs dictionary.
                inputs[key] = new_val
                st.session_state[key] = new_val
    return inputs

st.title("Test My Model Remotely!")
st.write("Input the required data, start execution, and give feedback!")
st.header("Project Parameters Input")

# Create input fields for each parameter
inputs = {}
for param in int_parameters:
    inputs[param] = st.number_input(param, min_value=0, step=1, format="%d")
for param in float_parameters_by_half:
    inputs[param] = st.number_input(param, min_value=0.0, step=0.5, format="%.1f")
for param in float_parameters_by_hundredth:
    inputs[param] = st.number_input(param, min_value=0.0, step=0.01, format="%.2f")
for param in bool_parameters:
    inputs[param] = st.checkbox(param)

# Create a container for displaying the updated JSON.
# This container can be updated rather than creating a new JSON display.
json_display = st.empty()
json_display.json(inputs)

# Optional: Button to load actual data from an Excel file.
# This updates the same JSON display with values from a random row.
if st.button("Use Actual Data"):
    actual_data = use_actual_data()
    inputs = update_inputs_from_actual_data(inputs, actual_data)
    json_display.json(inputs)

# Button to evaluate the model with the entered inputs
if st.button("Evaluate Model"):
    pass
    prediction = predict_cost(inputs)
    st.write("### Prediction:", prediction)
    log_prediction(inputs, prediction)
