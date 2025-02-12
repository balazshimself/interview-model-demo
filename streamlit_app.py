import json
import streamlit as st
from google.cloud import firestore
import pandas as pd
import random
import joblib

# Load the model saved in .sav format
model = joblib.load("xgboost_model.sav")

# Load Firestore credentials from Streamlit secrets
firestore_credentials = st.secrets["gcp_service_account"]
db = firestore.Client.from_service_account_info(firestore_credentials)
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

# Dummy prediction function – replace with your model's prediction code.
def predict_cost(features):
    # For demonstration, simply sum all numeric values
    total = 0.0
    for v in features.values():
        total += float(v)
    return total

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

# Create input fields dynamically
inputs = {}
for param, config in all_parameters.items():
    inputs[param] = st.number_input(
        param,
        min_value=float(config["min_value"]),  # Ensure min_value is a float
        max_value=float(config.get("max_value", float("inf"))),  # Ensure max_value is a float
        step=float(config["step"]),  # Ensure step is a float
        format=config["format"],
        value=float(st.session_state.inputs.get(param, config["min_value"]))  # Ensure value is a float
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
    log_prediction(inputs, prediction)

"""
import json
import streamlit as st
from google.cloud import firestore
import pandas as pd
import random
import joblib

# Load the model saved in .sav format
model = joblib.load("xgboost_model.sav")

# Load Firestore credentials from Streamlit secrets
firestore_credentials = st.secrets["gcp_service_account"]
db = firestore.Client.from_service_account_info(firestore_credentials)
df = pd.read_excel('SEERA_dataset.xlsx')

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
                # Update the inputs dictionary.
                inputs[key] = new_val
                st.session_state[key] = new_val
    return inputs

st.title("Test My Model Remotely!")
st.write("Input the required data, start execution, and give feedback!")
st.header("Project Parameters Input")

# Initialize session state
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}

# Create input fields for each parameter
inputs = {}

inputs["Dedicated team members"] = st.number_input("Dedicated team members", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Dedicated team members", 0))
inputs["Team size"] = st.number_input("Team size", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Team size", 0))
inputs["Object points"] = st.number_input("Object points", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Object points", 0))

inputs["Actual duration"] = st.number_input("Actual duration", min_value=0.0, step=0.5, format="%.1f", value=st.session_state.inputs.get("Actual duration", 0.0))
inputs["Estimated duration"] = st.number_input("Estimated duration", min_value=0.0, step=0.5, format="%.1f", value=st.session_state.inputs.get("Estimated duration", 0.0))

inputs["Degree of risk management"] = st.number_input("Degree of risk management", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Degree of risk management", 0))
inputs["Economic instability impact"] = st.number_input("Economic instability impact", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Economic instability impact", 0))
inputs["Development environment adequacy"] = st.number_input("Development environment adequacy", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Development environment adequacy", 0))
inputs["Estimated size"] = st.number_input("Estimated size", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Estimated size", 0))
inputs["Other sizing method"] = st.number_input("Other sizing method", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Other sizing method", 0))
inputs["Comments within the code"] = st.number_input("Comments within the code", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Comments within the code", 0))
inputs["Application domain"] = st.number_input("Application domain", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Application domain", 0))
inputs["Income satisfaction"] = st.number_input("Income satisfaction", min_value=0, step=1, format="%d", value=st.session_state.inputs.get("Income satisfaction", 0))
inputs["Top management opinion of previous system"] = st.number_input("Top management opinion of previous system", min_value=0, max_value=1, step=1, format="%d", value=st.session_state.inputs.get("Top management opinion of previous system", 0))

inputs["Requirement stability"] = st.number_input("Requirement stability", min_value=0.0, step=0.01, format="%.2f", value=st.session_state.inputs.get("Requirement stability", 0.0))

expected_keys = list(inputs.keys())

# Create a container for displaying the updated JSON.
# This container can be updated rather than creating a new JSON display.
json_display = st.empty()
json_display.json(inputs)

# Optional: Button to load actual data from an Excel file.
# This updates the same JSON display with values from a random row.
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
    log_prediction(inputs, prediction)
"""