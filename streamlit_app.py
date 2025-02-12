import json
import streamlit as st
from google.cloud import firestore
import pandas as pd
import random
import joblib

# Load the model saved in .sav format
model = joblib.load("xgboost_model_fixed.sav")

try:
    firestore_credentials = st.secrets["gcp_service_account"]
    db = firestore.Client.from_service_account_info(firestore_credentials)
except Exception as e:
    st.error(f"Failed to initialize Firestore client: {e}")
    st.stop()

df = pd.read_excel('SEERA_dataset.xlsx')

# Define all parameters in a single dictionary with their configurations
all_parameters = {
    'Dedicated team members': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Team size': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Object points': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Actual duration': {"min_value": 0.0, "step": 0.5, "format": "%.1f"},
    'Estimated duration': {"min_value": 0.0, "step": 0.5, "format": "%.1f"},
    'Degree of risk management': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Economic instability impact': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Development environment adequacy': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Estimated size': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Other sizing method': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Comments within the code': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Application domain': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Income satisfaction': {"min_value": 0.0, "step": 1.0, "format": "%.0f"},
    'Top management opinion of previous system': {"min_value": 0.0, "max_value": 1.0, "step": 1.0, "format": "%.0f"},
    'Requirement stability': {"min_value": 0.0, "step": 0.01, "format": "%.2f"}
}

# Function to log predictions
def log_prediction(inputs, prediction):
    log_data = {
        "features": inputs,
        "prediction": prediction,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("logs").add(log_data)  # Store in Firestore

# Finished predict function
def predict_cost(features):
    # For demonstration, simply sum all numeric values
    input_data = pd.DataFrame([features])
    input_data = input_data[list(features.keys())]
    prediction = model.predict(input_data)

    return prediction[0]

# Function to load a random row from an Excel file
def use_actual_data():
    row_dict = df.sample(n=1).to_dict(orient='records')[0]
    filtered_data = {key: value for key, value in row_dict.items() if key in all_parameters}
    return filtered_data

def update_inputs_from_actual_data(inputs, actual_data):
    for key, value in actual_data.items():
        if pd.notnull(value):
            try:
                new_val = float(value)  # Ensure the value is a float
            except (ValueError, TypeError):
                continue
            # Update the inputs dictionary and session state
            inputs[key] = new_val
            st.session_state[key] = new_val
    return inputs

st.title("Test My Model Remotely!")
st.write("Input the required data, start execution, and give feedback!")
st.header("Project Parameters Input")

# Initialize session state
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Create input fields dynamically
inputs = {}
for param, config in all_parameters.items():
    # Ensure min_value, max_value, and step are within JavaScript's safe range
    min_value = float(config["min_value"])
    max_value = float(config.get("max_value", float("inf")))
    step = float(config["step"])

    # Clamp min_value and max_value to JavaScript's safe range
    min_value = max(min_value, -1e15)  # Minimum safe value
    max_value = min(max_value, 1e15)   # Maximum safe value

    inputs[param] = st.number_input(
        param,
        min_value=min_value,
        max_value=max_value,
        step=step,
        format=config["format"],
        value=float(st.session_state.inputs.get(param, min_value))  # Ensure value is a float
    )

# Create a container for displaying the updated JSON.
json_display = st.empty()
json_display.json(inputs)

# Optional: Button to load actual data from an Excel file.
if st.button("Use Actual Data"):
    actual_data = use_actual_data()
    inputs = update_inputs_from_actual_data(inputs, actual_data)
    st.session_state.inputs = inputs
    json_display.json(inputs)
    st.rerun()

# Button to evaluate the model with the entered inputs
if st.button("Evaluate Model"):
    prediction = predict_cost(inputs)
    st.write("### Prediction:", prediction)

    # Store the prediction in session state
    st.session_state.prediction = prediction
    st.session_state.show_results = True  # Show the numeric field and submit button
    st.session_state.submitted = False  # Reset submission status

# Show the numeric field and submit button if the model has been evaluated
if st.session_state.show_results:
    st.session_state.actual_result = st.number_input(
        "Enter the actual result:",
        value=0.0,
        step=0.1,
        format="%.2f"
    )

    # Disable the submit button if there's no new data to submit
    if st.session_state.submitted:
        st.warning("Results already submitted. Re-evaluate the model to submit new results.")
    else:
        if st.button("Submit Results"):
            if "prediction" in st.session_state and "actual_result" in st.session_state:
                # Log the prediction and actual result to Firestore
                log_prediction(inputs, st.session_state.prediction, st.session_state.actual_result)
                st.session_state.submitted = True  # Mark as submitted
            else:
                st.error("Please evaluate the model and enter the actual result before submitting.")