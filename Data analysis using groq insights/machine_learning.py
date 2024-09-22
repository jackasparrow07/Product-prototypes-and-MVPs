import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score, f1_score
from sklearn.preprocessing import LabelEncoder
from pandas.api.types import is_numeric_dtype, is_categorical_dtype, is_object_dtype, is_string_dtype
import plotly.express as px
from data_utils import infer_data_type, check_and_preprocess

def encode_categorical(df):
    encoder = LabelEncoder()
    for col in df.columns:
        if infer_data_type(df[col]) in ['categorical', 'text']:
            df[col] = encoder.fit_transform(df[col].astype(str))
    return df

def perform_machine_learning(df):
    st.header("5. Machine Learning Features")
    
    # Encode categorical variables
    df_encoded = encode_categorical(df.copy())
    
    results = {}
    
    for target_column in df_encoded.columns:
        st.subheader(f"Analysis for target: {target_column}")
        
        try:
            X = df_encoded.drop(columns=[target_column])
            y = df_encoded[target_column]
            
            # Check if the target variable is suitable for machine learning
            target_type = infer_data_type(y)
            if target_type not in ['numeric', 'categorical']:
                st.warning(f"Skipping {target_column} as it's not suitable for machine learning (not numeric or categorical).")
                continue
            
            if target_type == 'categorical':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
            
            feature_importance = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
            feature_importance = feature_importance.sort_values('importance', ascending=False)
            
            st.plotly_chart(px.bar(feature_importance, x='feature', y='importance', title=f"Feature Importance for {target_column}"))
            
            y_pred = model.predict(X_test)
            
            if target_type == 'categorical':
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                st.write(f"Model Accuracy: {accuracy:.2f}")
                st.write(f"F1 Score: {f1:.2f}")
                performance = {'accuracy': accuracy, 'f1_score': f1}
            else:
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                st.write(f"Model Mean Squared Error: {mse:.2f}")
                st.write(f"R-squared Score: {r2:.2f}")
                performance = {'mse': mse, 'r2_score': r2}
            
            results[target_column] = {
                "feature_importance": feature_importance.to_dict(),
                "performance": performance
            }
        
        except Exception as e:
            st.error(f"An error occurred during machine learning tasks for {target_column}: {str(e)}")
            st.write(f"Data type of {target_column}: {infer_data_type(df_encoded[target_column])}")
            st.write(f"Unique values in {target_column}: {df_encoded[target_column].unique()}")
    
    return results