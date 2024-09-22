import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import io
import base64
import sweetviz as sv
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype, is_categorical_dtype, is_object_dtype
from groq_integration import validate_api_key, fetch_groq_models, get_groq_insights
from data_loader import load_data, display_data_overview
from data_preprocessing import preprocess_data, preprocess_column
from exploratory_analysis import perform_eda
from advanced_visualizations import create_advanced_visualizations
from machine_learning import perform_machine_learning
from export_options import export_report

# Set page configuration
st.set_page_config(page_title="Comprehensive EDA App", layout="wide")

# Custom CSS for improved UI/UX
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    }
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .Widget>label {
        color: #2c3e50;
        font-weight: 600;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #3498db;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 5px;
        border: 1px solid #bdc3c7;
        padding: 8px 12px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Main app logic
st.title("Comprehensive EDA and Data Analysis App with LLM Intelligence")

# Groq API integration
api_key = st.text_input("Enter your Groq API key:", type="password")
if api_key:
    if validate_api_key(api_key):
        st.success("API key validated successfully!")
        models = fetch_groq_models(api_key)
        selected_model = st.selectbox("Select Groq model:", 
                                      [m for m in models if "gemini 2 9b" in m.lower() or "mixtral" in m.lower()])
    else:
        st.error("Invalid API key. Please try again.")

st.header("1. File Upload and Data Quality Assessment")

uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        # Convert problematic columns to appropriate types
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype('string')
            elif df[col].dtype == 'int64':
                df[col] = df[col].astype('Int64')  # nullable integer type

        # Get AI insights on the data
        initial_insights = get_groq_insights(api_key, selected_model, df.head().to_string())
        st.subheader("AI Insights on Data")
        st.write(initial_insights)
        
        # Display data overview
        display_data_overview(df)
        
        # Intelligent data preprocessing
        with st.spinner("Preprocessing data..."):
            original_df = df.copy()  # Keep a copy of the original dataset
            df = df.apply(preprocess_column)
        
        # Data preprocessing
        df = preprocess_data(df)
        
        # Get AI insights on preprocessed data
        preprocessed_insights = get_groq_insights(api_key, selected_model, df.head().to_string())
        st.subheader("AI Insights on Preprocessed Data")
        st.write(preprocessed_insights)
        
        # Exploratory Data Analysis
        eda_results = perform_eda(df)
        
        # Get AI insights on EDA results
        eda_insights = get_groq_insights(api_key, selected_model, str(eda_results))
        st.subheader("AI Insights on Exploratory Data Analysis")
        st.write(eda_insights)
        
        # Advanced Visualizations
        advanced_viz_results = create_advanced_visualizations(df)
        
        # Get AI insights on advanced visualizations
        viz_insights = get_groq_insights(api_key, selected_model, str(advanced_viz_results))
        st.subheader("AI Insights on Advanced Visualizations")
        st.write(viz_insights)
        
        # Machine Learning Features
        ml_results = perform_machine_learning(df)
        
        if ml_results:
            # Get AI insights on machine learning results
            ml_insights = get_groq_insights(api_key, selected_model, str(ml_results))
            st.subheader("AI Insights on Machine Learning Results")
            st.write(ml_insights)
        
        # Export Options
        export_report(df, eda_results, advanced_viz_results, ml_results)
        
        # Allow user to ask for specific insights
        user_question = st.text_input("Ask for specific insights:")
        if user_question:
            specific_insights = get_groq_insights(api_key, selected_model, f"{user_question}\n\nContext:\n{df.head().to_string()}")
            st.subheader("Specific Insights")
            st.write(specific_insights)

else:
    st.info("Please upload a CSV or XLSX file to begin the analysis.")