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

# Helper functions for intelligent data handling
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
        return series

def encode_categorical(df):
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    for col in df.select_dtypes(include=['category', 'object']):
        df[col] = encoder.fit_transform(df[[col]]).astype(int)
    return df

# Main app logic
st.title("Comprehensive EDA and Data Analysis App")

st.header("1. File Upload and Data Quality Assessment")

uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)
        
        if df.empty:
            st.error("The uploaded file is empty. Please upload a file with data.")
        elif len(df.columns) == 0:
            st.error("No columns found in the uploaded file. Please check the file format.")
        else:
            st.success("File successfully uploaded and read!")
            
            # Intelligent data preprocessing
            with st.spinner("Preprocessing data..."):
                original_df = df.copy()  # Keep a copy of the original dataset
                df = df.apply(preprocess_column)
            
            # Display basic information about the dataset
            st.subheader("Dataset Overview")
            st.write(f"Number of rows: {df.shape[0]}")
            st.write(f"Number of columns: {df.shape[1]}")

            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.notnull().sum(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.write(col_info)
            
            # Display first few rows
            st.subheader("First Few Rows of the Dataset")
            st.write(df.head())
            
            # 2. Data Cleaning and Preprocessing
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
            
            if missing_strategy == "Keep missing data":
                st.info("Missing data kept as is.")
            elif missing_strategy == "Remove rows with missing data":
                df = df.dropna()
                st.success("Rows with missing data removed.")
            elif missing_strategy == "Fill missing data with mean/mode":
                for column in df.columns:
                    if is_numeric_dtype(df[column]):
                        imputer = SimpleImputer(strategy='mean')
                    else:
                        imputer = SimpleImputer(strategy='most_frequent')
                    df[column] = imputer.fit_transform(df[[column]])
                st.success("Missing data filled with mean/mode.")
            else:
                for column in df.columns:
                    if is_numeric_dtype(df[column]):
                        imputer = SimpleImputer(strategy='median')
                    else:
                        imputer = SimpleImputer(strategy='most_frequent')
                    df[column] = imputer.fit_transform(df[[column]])
                st.success("Missing data filled with median/mode.")
            
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
                    
                    if outlier_strategy == "Remove outliers":
                        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                        st.success(f"Outliers removed from '{column}'.")
                    elif outlier_strategy == "Cap outliers":
                        df[column] = df[column].clip(lower_bound, upper_bound)
                        st.success(f"Outliers capped in '{column}'.")
                    else:
                        st.info(f"Outliers kept in '{column}'.")
            
            # 3. Exploratory Data Analysis
            st.header("3. Exploratory Data Analysis")
            
            # Summary statistics
            st.subheader("Summary Statistics")
            st.write(df.describe(include='all'))
            
            # Correlation matrix
            st.subheader("Correlation Matrix")
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)
            else:
                st.warning("No numeric columns found for correlation analysis.")
            
            # Distribution plots
            st.subheader("Distribution Plots")
            for column in df.columns:
                if is_numeric_dtype(df[column]):
                    fig = px.histogram(df, x=column, marginal="box", title=f"Distribution of {column}")
                    st.plotly_chart(fig)
                    
                    skewness = df[column].skew()
                    kurtosis = df[column].kurtosis()
                    st.markdown(f"""
                    📊 Distribution insights for {column}:
                    - 📏 Skewness: {skewness:.2f} 
                    - 📈 Kurtosis: {kurtosis:.2f}
                    """)
                elif is_categorical_dtype(df[column]) or is_object_dtype(df[column]):
                    value_counts = df[column].value_counts().reset_index()
                    value_counts.columns = ['category', 'count']
                    fig = px.bar(value_counts, x='category', y='count', title=f"Distribution of {column}")
                    st.plotly_chart(fig)
                else:
                    st.write(f"Cannot create distribution plot for column '{column}' due to its data type.")
            
            # 4. Advanced Visualizations
            st.header("4. Advanced Visualizations")
            
            # Scatter plots
            st.subheader("Scatter Plots")
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) >= 2:
                x_column = st.selectbox("Select X-axis column for scatter plot:", numeric_columns)
                y_column = st.selectbox("Select Y-axis column for scatter plot:", numeric_columns)
                fig = px.scatter(df, x=x_column, y=y_column, 
                                 title=f"Scatter plot: {x_column} vs {y_column}",
                                 hover_data=df.columns)
                st.plotly_chart(fig)
            else:
                st.warning("Not enough numeric columns for scatter plot.")
            
            # Time series analysis (if applicable)
            date_columns = df.select_dtypes(include=['datetime64']).columns
            if len(date_columns) > 0:
                st.subheader("Time Series Analysis")
                date_column = st.selectbox("Select date column for time series analysis:", date_columns)
                value_column = st.selectbox("Select value column for time series analysis:", numeric_columns)
                
                df_ts = df.set_index(date_column)
                fig = px.line(df_ts, y=value_column, title=f"Time Series: {value_column} over time")
                st.plotly_chart(fig)
            
            # 5. Machine Learning Features
            st.header("5. Machine Learning Features")
            
            # Feature importance
            st.subheader("Feature Importance")
            target_column = st.selectbox("Select target column for feature importance:", df.columns)
            
            # Encode categorical variables
            df_encoded = encode_categorical(df.copy())
            
            try:
                X = df_encoded.drop(columns=[target_column])
                y = df_encoded[target_column]
                
                if is_object_dtype(y) or is_categorical_dtype(y):
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                model.fit(X, y)
                feature_importance = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
                feature_importance = feature_importance.sort_values('importance', ascending=False)
                
                fig = px.bar(feature_importance, x='feature', y='importance', title="Feature Importance")
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"An error occurred while calculating feature importance: {str(e)}")
            
            # Simple prediction
            st.subheader("Simple Prediction")
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                if is_object_dtype(y) or is_categorical_dtype(y):
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    accuracy = accuracy_score(y_test, y_pred)
                    st.write(f"Model Accuracy: {accuracy:.2f}")
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    mse = mean_squared_error(y_test, y_pred)
                    st.write(f"Model Mean Squared Error: {mse:.2f}")
            except Exception as e:
                st.error(f"An error occurred during model training and prediction: {str(e)}")
            
            # 6. Export Options
            st.header("6. Export Options")
            
            # Export options
            export_format = st.selectbox("Choose export format:", (".md", ".csv", ".png", ".svg", ".txt"))
            
            if st.button("Generate and Download Report"):
                if export_format == ".md":
                    markdown_report = f"""
                    # Data Analysis Report

                    ## Dataset Overview
                    - Number of rows: {original_df.shape[0]}
                    - Number of columns: {original_df.shape[1]}

                    ## Summary Statistics
                    {df.describe(include='all').to_markdown()}

                    ## Correlation Matrix
                    {corr_matrix.to_markdown() if 'corr_matrix' in locals() else "No correlation matrix available."}

                    ## Feature Importance
                    {feature_importance.to_markdown() if 'feature_importance' in locals() else "Feature importance not calculated."}
                    """
                    b64 = base64.b64encode(markdown_report.encode()).decode()
                    href = f'<a href="data:text/markdown;base64,{b64}" download="report.md">Download Markdown report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                elif export_format == ".csv":
                    try:
                        csv = original_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"An error occurred while exporting to CSV: {str(e)}")
                elif export_format in (".png", ".svg"):
                    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
                    df.select_dtypes(include=[np.number]).hist(ax=axs[0, 0])
                    axs[0, 0].set_title("Histograms")
                    if 'corr_matrix' in locals():
                        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=axs[0, 1])
                        axs[0, 1].set_title("Correlation Matrix")
                    if 'feature_importance' in locals():
                        feature_importance.plot(kind='bar', x='feature', y='importance', ax=axs[1, 0])
                        axs[1, 0].set_title("Feature Importance")
                    df.select_dtypes(include=[np.number]).boxplot(ax=axs[1, 1])
                    axs[1, 1].set_title("Box Plots")
                    plt.tight_layout()
                    
                    img = io.BytesIO()
                    plt.savefig(img, format=export_format[1:])
                    img.seek(0)
                    b64 = base64.b64encode(img.getvalue()).decode()
                    href = f'<a href="data:image/{export_format[1:]};base64,{b64}" download="summary_plot{export_format}">Download {export_format.upper()} Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:  # .txt
                    text_report = f"""
                    Dataset Summary:
                    Number of rows: {df.shape[0]}
                    Number of columns: {df.shape[1]}
                    
                    Column Information:
                    {col_info.to_string()}
                    
                    Summary Statistics:
                    {df.describe(include='all').to_string()}
                    
                    Feature Importance:
                    {feature_importance.to_string() if 'feature_importance' in locals() else "Feature importance not calculated."}
                    """
                    b64 = base64.b64encode(text_report.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="report.txt">Download TXT report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                st.success("Report generated and ready for download!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your file and try again. If the problem persists, contact support.")
else:
    st.info("Please upload a CSV or XLSX file to begin the analysis.")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)
        
        if df.empty:
            st.error("The uploaded file is empty. Please upload a file with data.")
        elif len(df.columns) == 0:
            st.error("No columns found in the uploaded file. Please check the file format.")
        else:
            st.success("File successfully uploaded and read!")
            
            # Intelligent data preprocessing
            with st.spinner("Preprocessing data..."):
                original_df = df.copy()  # Keep a copy of the original dataset
                df = df.apply(preprocess_column)
            
            # Display basic information about the dataset
            st.subheader("Dataset Overview")
            st.write(f"Number of rows: {df.shape[0]}")
            st.write(f"Number of columns: {df.shape[1]}")

            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.notnull().sum(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.write(col_info)
            
            # Display first few rows
            st.subheader("First Few Rows of the Dataset")
            st.write(df.head())
            
            # 2. Data Cleaning and Preprocessing
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
            
            if missing_strategy == "Keep missing data":
                st.info("Missing data kept as is.")
            elif missing_strategy == "Remove rows with missing data":
                df = df.dropna()
                st.success("Rows with missing data removed.")
            elif missing_strategy == "Fill missing data with mean/mode":
                for column in df.columns:
                    if is_numeric_dtype(df[column]):
                        imputer = SimpleImputer(strategy='mean')
                    else:
                        imputer = SimpleImputer(strategy='most_frequent')
                    df[column] = imputer.fit_transform(df[[column]])
                st.success("Missing data filled with mean/mode.")
            else:
                for column in df.columns:
                    if is_numeric_dtype(df[column]):
                        imputer = SimpleImputer(strategy='median')
                    else:
                        imputer = SimpleImputer(strategy='most_frequent')
                    df[column] = imputer.fit_transform(df[[column]])
                st.success("Missing data filled with median/mode.")
            
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
                    
                    if outlier_strategy == "Remove outliers":
                        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                        st.success(f"Outliers removed from '{column}'.")
                    elif outlier_strategy == "Cap outliers":
                        df[column] = df[column].clip(lower_bound, upper_bound)
                        st.success(f"Outliers capped in '{column}'.")
                    else:
                        st.info(f"Outliers kept in '{column}'.")
            
            # 3. Exploratory Data Analysis
            st.header("3. Exploratory Data Analysis")
            
            # Summary statistics
            st.subheader("Summary Statistics")
            st.write(df.describe(include='all'))
            
            # Correlation matrix
            st.subheader("Correlation Matrix")
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)
            else:
                st.warning("No numeric columns found for correlation analysis.")
            
            # Distribution plots
            st.subheader("Distribution Plots")
            for column in df.columns:
                if is_numeric_dtype(df[column]):
                    fig = px.histogram(df, x=column, marginal="box", title=f"Distribution of {column}")
                    st.plotly_chart(fig)
                    
                    skewness = df[column].skew()
                    kurtosis = df[column].kurtosis()
                    st.markdown(f"""
                    📊 Distribution insights for {column}:
                    - 📏 Skewness: {skewness:.2f} 
                    - 📈 Kurtosis: {kurtosis:.2f}
                    """)
                elif is_categorical_dtype(df[column]) or is_object_dtype(df[column]):
                    value_counts = df[column].value_counts().reset_index()
                    value_counts.columns = ['category', 'count']
                    fig = px.bar(value_counts, x='category', y='count', title=f"Distribution of {column}")
                    st.plotly_chart(fig)
                else:
                    st.write(f"Cannot create distribution plot for column '{column}' due to its data type.")
            
            # 4. Advanced Visualizations
            st.header("4. Advanced Visualizations")
            
            # Scatter plots
            st.subheader("Scatter Plots")
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) >= 2:
                x_column = st.selectbox("Select X-axis column for scatter plot:", numeric_columns)
                y_column = st.selectbox("Select Y-axis column for scatter plot:", numeric_columns)
                fig = px.scatter(df, x=x_column, y=y_column, 
                                 title=f"Scatter plot: {x_column} vs {y_column}",
                                 hover_data=df.columns)
                st.plotly_chart(fig)
            else:
                st.warning("Not enough numeric columns for scatter plot.")
            
            # Time series analysis (if applicable)
            date_columns = df.select_dtypes(include=['datetime64']).columns
            if len(date_columns) > 0:
                st.subheader("Time Series Analysis")
                date_column = st.selectbox("Select date column for time series analysis:", date_columns)
                value_column = st.selectbox("Select value column for time series analysis:", numeric_columns)
                
                df_ts = df.set_index(date_column)
                fig = px.line(df_ts, y=value_column, title=f"Time Series: {value_column} over time")
                st.plotly_chart(fig)
            
            # 5. Machine Learning Features
            st.header("5. Machine Learning Features")
            
            # Feature importance
            st.subheader("Feature Importance")
            target_column = st.selectbox("Select target column for feature importance:", df.columns)
            
            # Encode categorical variables
            df_encoded = encode_categorical(df.copy())
            
            try:
                X = df_encoded.drop(columns=[target_column])
                y = df_encoded[target_column]
                
                if is_object_dtype(y) or is_categorical_dtype(y):
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                model.fit(X, y)
                feature_importance = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
                feature_importance = feature_importance.sort_values('importance', ascending=False)
                
                fig = px.bar(feature_importance, x='feature', y='importance', title="Feature Importance")
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"An error occurred while calculating feature importance: {str(e)}")
            
            # Simple prediction
            st.subheader("Simple Prediction")
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                if is_object_dtype(y) or is_categorical_dtype(y):
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    accuracy = accuracy_score(y_test, y_pred)
                    st.write(f"Model Accuracy: {accuracy:.2f}")
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    mse = mean_squared_error(y_test, y_pred)
                    st.write(f"Model Mean Squared Error: {mse:.2f}")
            except Exception as e:
                st.error(f"An error occurred during model training and prediction: {str(e)}")
            
            # 6. Export Options
            st.header("6. Export Options")
            
            # Export options
            export_format = st.selectbox("Choose export format:", (".md", ".csv", ".png", ".svg", ".txt"))
            
            if st.button("Generate and Download Report"):
                if export_format == ".md":
                    markdown_report = f"""
                    # Data Analysis Report

                    ## Dataset Overview
                    - Number of rows: {original_df.shape[0]}
                    - Number of columns: {original_df.shape[1]}

                    ## Summary Statistics
                    {df.describe(include='all').to_markdown()}

                    ## Correlation Matrix
                    {corr_matrix.to_markdown() if 'corr_matrix' in locals() else "No correlation matrix available."}

                    ## Feature Importance
                    {feature_importance.to_markdown() if 'feature_importance' in locals() else "Feature importance not calculated."}
                    """
                    b64 = base64.b64encode(markdown_report.encode()).decode()
                    href = f'<a href="data:text/markdown;base64,{b64}" download="report.md">Download Markdown report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                elif export_format == ".csv":
                    try:
                        csv = original_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"An error occurred while exporting to CSV: {str(e)}")
                elif export_format in (".png", ".svg"):
                    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
                    df.select_dtypes(include=[np.number]).hist(ax=axs[0, 0])
                    axs[0, 0].set_title("Histograms")
                    if 'corr_matrix' in locals():
                        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=axs[0, 1])
                        axs[0, 1].set_title("Correlation Matrix")
                    if 'feature_importance' in locals():
                        feature_importance.plot(kind='bar', x='feature', y='importance', ax=axs[1, 0])
                        axs[1, 0].set_title("Feature Importance")
                    df.select_dtypes(include=[np.number]).boxplot(ax=axs[1, 1])
                    axs[1, 1].set_title("Box Plots")
                    plt.tight_layout()
                    
                    img = io.BytesIO()
                    plt.savefig(img, format=export_format[1:])
                    img.seek(0)
                    b64 = base64.b64encode(img.getvalue()).decode()
                    href = f'<a href="data:image/{export_format[1:]};base64,{b64}" download="summary_plot{export_format}">Download {export_format.upper()} Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:  # .txt
                    text_report = f"""
                    Dataset Summary:
                    Number of rows: {df.shape[0]}
                    Number of columns: {df.shape[1]}
                    
                    Column Information:
                    {col_info.to_string()}
                    
                    Summary Statistics:
                    {df.describe(include='all').to_string()}
                    
                    Feature Importance:
                    {feature_importance.to_string() if 'feature_importance' in locals() else "Feature importance not calculated."}
                    """
                    b64 = base64.b64encode(text_report.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="report.txt">Download TXT report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                st.success("Report generated and ready for download!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your file and try again. If the problem persists, contact support.")
else:
    st.info("Please upload a CSV or XLSX file to begin the analysis.")