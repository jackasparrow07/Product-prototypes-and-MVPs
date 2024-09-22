import streamlit as st
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype, is_categorical_dtype, is_object_dtype

def infer_data_type(series):
    if is_numeric_dtype(series):
        return 'numeric'
    elif is_datetime64_any_dtype(series):
        return 'datetime'
    elif is_categorical_dtype(series) or (is_object_dtype(series) and series.nunique() / len(series) < 0.5):
        return 'categorical'
    else:
        return 'text'

def preprocess_column(series):
    data_type = infer_data_type(series)
    if data_type == 'numeric':
        return pd.to_numeric(series, errors='coerce')
    elif data_type == 'datetime':
        return pd.to_datetime(series, errors='coerce')
    elif data_type == 'categorical':
        return series.astype('category')
    else:
        return series.astype('string')

def handle_missing_data(df, strategy):
    for column in df.columns:
        data_type = infer_data_type(df[column])
        if data_type == 'numeric':
            if strategy == "Remove rows with missing data":
                df = df.dropna(subset=[column])
            elif strategy in ["Fill missing data with mean/mode", "Fill missing data with median"]:
                imputer = SimpleImputer(strategy='mean' if strategy == "Fill missing data with mean/mode" else 'median')
                df[column] = imputer.fit_transform(df[[column]])
        elif data_type in ['categorical', 'text']:
            if strategy == "Remove rows with missing data":
                df = df.dropna(subset=[column])
            elif strategy in ["Fill missing data with mean/mode", "Fill missing data with median"]:
                imputer = SimpleImputer(strategy='most_frequent')
                df[column] = imputer.fit_transform(df[[column]])
    
    st.success(f"Missing data handled using strategy: {strategy}")
    return df

def handle_outliers(df, column, strategy):
    if infer_data_type(df[column]) != 'numeric':
        st.warning(f"Outlier detection skipped for non-numeric column: {column}")
        return df
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    if strategy == "Remove outliers":
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        st.success(f"Outliers removed from '{column}'.")
    elif strategy == "Cap outliers":
        df[column] = df[column].clip(lower_bound, upper_bound)
        st.success(f"Outliers capped in '{column}'.")
    else:
        st.info(f"Outliers kept in '{column}'.")
    return df

def preprocess_data(df):
    st.header("2. Data Cleaning and Preprocessing")
    
    # Handling missing data
    st.subheader("Handling Missing Data")
    missing_data = df.isnull().sum()
    st.write("Missing values in each column:")
    st.write(missing_data)
    
    missing_strategy = st.selectbox(
        "Choose strategy for handling missing data:",
        ("Keep missing data", "Remove rows with missing data", "Fill missing data with mean/mode", "Fill missing data with median")
    )
    
    df = handle_missing_data(df, missing_strategy)
    
    # Handling outliers
    st.subheader("Outlier Detection and Handling")
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    for column in numeric_columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        
        if not outliers.empty:
            st.write(f"Outliers detected in column '{column}':")
            st.write(outliers)
            
            outlier_strategy = st.selectbox(
                f"Choose strategy for handling outliers in '{column}':",
                ("Keep outliers", "Remove outliers", "Cap outliers")
            )
            
            df = handle_outliers(df, column, outlier_strategy)
    
    return df