import pandas as pd
import streamlit as st
from data_utils import infer_data_type, preprocess_column, check_and_preprocess

def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)
        
        if df.empty:
            st.error("The uploaded file is empty. Please upload a file with data.")
            return None
        elif len(df.columns) == 0:
            st.error("No columns found in the uploaded file. Please check the file format.")
            return None
        else:
            # Convert problematic columns to appropriate types
            for col in df.columns:
                try:
                    df[col] = preprocess_column(df[col])
                except Exception as e:
                    st.warning(f"Could not preprocess column '{col}': {str(e)}")
            
            st.success("File successfully uploaded and read!")
            return df
    except Exception as e:
        st.error(f"An error occurred while loading the file: {str(e)}")
        return None

def display_data_overview(df):
    st.subheader("Dataset Overview")
    st.write(f"Number of rows: {df.shape[0]}")
    st.write(f"Number of columns: {df.shape[1]}")

    st.subheader("Column Information")
    col_info = pd.DataFrame({
        'Column Name': df.columns,
        'Data Type': df.dtypes,
        'Inferred Type': df.apply(infer_data_type),
        'Non-Null Count': df.notnull().sum(),
        'Null Count': df.isnull().sum(),
        'Unique Values': df.nunique()
    })
    st.write(col_info)
    
    st.subheader("First Few Rows of the Dataset")
    st.write(df.head())

    # Add data quality checks
    st.subheader("Data Quality Checks")
    for col in df.columns:
        data_type = infer_data_type(df[col])
        if data_type == 'numeric':
            if df[col].isnull().sum() > 0:
                st.warning(f"Column '{col}' contains {df[col].isnull().sum()} null values.")
            if df[col].min() < 0 and df[col].max() > 0:
                st.info(f"Column '{col}' contains both positive and negative values.")
        elif data_type == 'datetime':
            if df[col].isnull().sum() > 0:
                st.warning(f"Column '{col}' contains {df[col].isnull().sum()} null values.")
            st.info(f"Date range for '{col}': {df[col].min()} to {df[col].max()}")
        elif data_type in ['categorical', 'text']:
            if df[col].isnull().sum() > 0:
                st.warning(f"Column '{col}' contains {df[col].isnull().sum()} null values.")
            if df[col].nunique() == 1:
                st.warning(f"Column '{col}' has only one unique value: {df[col].unique()[0]}")