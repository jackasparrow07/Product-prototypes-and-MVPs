import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from data_utils import infer_data_type, check_and_preprocess

def perform_eda(df):
    st.header("3. Exploratory Data Analysis")
    
    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(df.describe(include='all'))
    
    # Correlation matrix
    st.subheader("Correlation Matrix")
    try:
        numeric_df = check_and_preprocess(df, {col: 'numeric' for col in df.columns if infer_data_type(df[col]) == 'numeric'})
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No numeric columns found for correlation analysis.")
    except ValueError as e:
        st.warning(f"Could not create correlation matrix: {str(e)}")
    
    # Distribution plots
    st.subheader("Distribution Plots")
    for column in df.columns:
        data_type = infer_data_type(df[column])
        if data_type == 'numeric':
            try:
                numeric_col = check_and_preprocess(df, {column: 'numeric'})
                fig = px.histogram(numeric_col, x=column, marginal="box", title=f"Distribution of {column}")
                st.plotly_chart(fig)
                
                skewness = numeric_col[column].skew()
                kurtosis = numeric_col[column].kurtosis()
                st.markdown(f"""
                📊 Distribution insights for {column}:
                - 📏 Skewness: {skewness:.2f} 
                - 📈 Kurtosis: {kurtosis:.2f}
                """)
            except ValueError as e:
                st.warning(f"Could not create distribution plot for {column}: {str(e)}")
        elif data_type in ['categorical', 'text']:
            try:
                cat_col = check_and_preprocess(df, {column: 'categorical'})
                value_counts = cat_col[column].value_counts().reset_index()
                value_counts.columns = ['category', 'count']
                fig = px.bar(value_counts, x='category', y='count', title=f"Distribution of {column}")
                st.plotly_chart(fig)
            except ValueError as e:
                st.warning(f"Could not create distribution plot for {column}: {str(e)}")
    
    return {
        "correlation_matrix": corr_matrix.to_dict() if 'corr_matrix' in locals() else None,
        "numeric_columns": numeric_df.columns.tolist() if 'numeric_df' in locals() else []
    }