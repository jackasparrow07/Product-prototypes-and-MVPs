import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_utils import infer_data_type, check_and_preprocess

def create_advanced_visualizations(df):
    st.header("4. Advanced Visualizations")
    
    numeric_columns = [col for col in df.columns if infer_data_type(df[col]) == 'numeric']
    date_columns = [col for col in df.columns if infer_data_type(df[col]) == 'datetime']
    
    # Scatter plots
    st.subheader("Scatter Plots")
    if len(numeric_columns) >= 2:
        for i in range(min(5, len(numeric_columns) - 1)):  # Create up to 5 scatter plots
            x_column = numeric_columns[i]
            y_column = numeric_columns[i + 1]
            try:
                scatter_df = check_and_preprocess(df, {x_column: 'numeric', y_column: 'numeric'})
                fig = px.scatter(scatter_df, x=x_column, y=y_column, 
                                 title=f"Scatter plot: {x_column} vs {y_column}",
                                 hover_data=df.columns)
                st.plotly_chart(fig)
            except ValueError as e:
                st.warning(f"Could not create scatter plot for {x_column} vs {y_column}: {str(e)}")
    else:
        st.warning("Not enough numeric columns for scatter plots.")
    
    # Time series analysis (if applicable)
    if len(date_columns) > 0 and len(numeric_columns) > 0:
        st.subheader("Time Series Analysis")
        date_column = date_columns[0]
        for value_column in numeric_columns[:3]:  # Create up to 3 time series plots
            try:
                ts_df = check_and_preprocess(df, {date_column: 'datetime', value_column: 'numeric'})
                ts_df = ts_df.set_index(date_column)
                fig = px.line(ts_df, y=value_column, title=f"Time Series: {value_column} over time")
                st.plotly_chart(fig)
            except ValueError as e:
                st.warning(f"Could not create time series plot for {value_column}: {str(e)}")
    
    # Pair plot
    st.subheader("Pair Plot")
    if len(numeric_columns) > 1:
        selected_columns = numeric_columns[:4]  # Select up to 4 columns for the pair plot
        try:
            pair_df = check_and_preprocess(df, {col: 'numeric' for col in selected_columns})
            fig = px.scatter_matrix(pair_df[selected_columns])
            st.plotly_chart(fig)
        except ValueError as e:
            st.warning(f"Could not create pair plot: {str(e)}")
    else:
        st.warning("Not enough numeric columns for pair plot.")
    
    # 3D Scatter plot
    st.subheader("3D Scatter Plot")
    if len(numeric_columns) >= 3:
        x_column, y_column, z_column = numeric_columns[:3]
        try:
            scatter_3d_df = check_and_preprocess(df, {x_column: 'numeric', y_column: 'numeric', z_column: 'numeric'})
            fig = px.scatter_3d(scatter_3d_df, x=x_column, y=y_column, z=z_column, 
                                title=f"3D Scatter plot: {x_column} vs {y_column} vs {z_column}")
            st.plotly_chart(fig)
        except ValueError as e:
            st.warning(f"Could not create 3D scatter plot: {str(e)}")
    else:
        st.warning("Not enough numeric columns for 3D scatter plot.")
    
    return {
        "scatter_plots": [f"{numeric_columns[i]} vs {numeric_columns[i+1]}" for i in range(min(5, len(numeric_columns) - 1))],
        "time_series": [f"{col} over time" for col in numeric_columns[:3]] if len(date_columns) > 0 else None,
        "pair_plot": ", ".join(selected_columns) if 'selected_columns' in locals() else None,
        "3d_scatter": f"{x_column} vs {y_column} vs {z_column}" if 'z_column' in locals() else None
    }