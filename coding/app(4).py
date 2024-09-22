import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import openpyxl
import textract
import nltk
from wordcloud import WordCloud
import io
import os
from collections import Counter
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import spacy

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to read various file types
def read_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension == '.txt':
        return file.getvalue().decode('utf-8')
    elif file_extension == '.docx':
        doc = Document(io.BytesIO(file.getvalue()))
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file, engine='openpyxl')
        return df
    elif file_extension == '.csv':
        df = pd.read_csv(file)
        return df
    elif file_extension == '.md':
        return file.getvalue().decode('utf-8')
    else:
        # For other file types, use textract
        return textract.process(io.BytesIO(file.getvalue())).decode('utf-8')

# Function to clean and preprocess text data
def clean_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = ''.join([char for char in text if char.isalnum() or char.isspace()])
    # Remove stopwords
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

# Function to perform EDA on text data
def text_eda(text):
    words = text.split()
    word_counts = Counter(words)
    
    # Most common words
    common_words = word_counts.most_common(10)
    
    # Word frequency distribution
    word_freq_df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Frequency'])
    word_freq_df = word_freq_df.sort_values('Frequency', ascending=False)
    
    return common_words, word_freq_df

# Function to preprocess tabular data
def preprocess_tabular_data(df):
    # Create a copy of the dataframe
    df_processed = df.copy()
    
    # Identify numeric and categorical columns
    numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
    categorical_columns = df_processed.select_dtypes(exclude=[np.number]).columns
    
    # Handle missing values
    imputer = SimpleImputer(strategy='mean')
    df_processed[numeric_columns] = imputer.fit_transform(df_processed[numeric_columns])
    
    # Encode categorical variables
    label_encoder = LabelEncoder()
    for col in categorical_columns:
        df_processed[col] = label_encoder.fit_transform(df_processed[col].astype(str))
    
    # Scale numeric features
    scaler = StandardScaler()
    df_processed[numeric_columns] = scaler.fit_transform(df_processed[numeric_columns])
    
    return df_processed, numeric_columns, categorical_columns

# Function to perform EDA on tabular data
def tabular_eda(df):
    # Preprocess the data
    df_processed, numeric_columns, categorical_columns = preprocess_tabular_data(df)
    
    # Basic statistics
    basic_stats = df_processed.describe()
    
    # Missing values
    missing_values = df.isnull().sum()
    
    # Correlation matrix (only for numeric columns)
    correlation_matrix = df_processed[numeric_columns].corr()
    
    return basic_stats, missing_values, correlation_matrix, df_processed, numeric_columns, categorical_columns

# Function to generate word cloud
def generate_word_cloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# Function to generate interactive bar chart
def generate_interactive_bar_chart(data, title, x_label, y_label):
    fig = px.bar(data, x=data.index, y=data.values, title=title,
                 labels={'x': x_label, 'y': y_label},
                 hover_data={'value': ':.2f'})
    fig.update_layout(hovermode='closest')
    return fig

# Function to generate interactive line chart
def generate_interactive_line_chart(data, title, x_label, y_label):
    fig = px.line(data, x=data.index, y=data.values, title=title,
                  labels={'x': x_label, 'y': y_label},
                  hover_data={'value': ':.2f'})
    fig.update_layout(hovermode='x unified')
    return fig

# Function to generate interactive pie chart
def generate_interactive_pie_chart(data, title):
    fig = px.pie(values=data.values, names=data.index, title=title,
                 hover_data={'value': ':.2f'})
    return fig

# Function to generate interactive heatmap
def generate_interactive_heatmap(data, title):
    fig = px.imshow(data, title=title, labels=dict(color="Correlation"))
    fig.update_layout(height=600, width=600)
    return fig

# Function to extract context from text
def extract_context(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Function to generate context-based visualizations
def generate_context_visualizations(df, context):
    visualizations = []
    
    for entity, label in context:
        if label == 'DATE':
            # Time series analysis
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                time_series = df.set_index('date').resample('M').mean()
                fig = generate_interactive_line_chart(time_series, f"Time Series Analysis - {entity}", "Date", "Value")
                visualizations.append(("Time Series", fig))
        
        elif label == 'ORG':
            # Organization-based analysis
            if 'organization' in df.columns:
                org_data = df[df['organization'] == entity].mean()
                fig = generate_interactive_bar_chart(org_data, f"Analysis for {entity}", "Metric", "Value")
                visualizations.append((f"Organization: {entity}", fig))
        
        elif label == 'MONEY':
            # Financial analysis
            financial_cols = [col for col in df.columns if 'price' in col.lower() or 'cost' in col.lower() or 'revenue' in col.lower()]
            if financial_cols:
                financial_data = df[financial_cols].sum()
                fig = generate_interactive_pie_chart(financial_data, f"Financial Breakdown - {entity}")
                visualizations.append(("Financial Analysis", fig))
    
    return visualizations

# Main Streamlit app
def main():
    st.title("Enhanced Data Analyst E2E App")
    
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'docx', 'xlsx', 'xls', 'csv', 'md'])
    
    if uploaded_file is not None:
        file_contents = read_file(uploaded_file)
        
        st.subheader("File Contents")
        if isinstance(file_contents, pd.DataFrame):
            st.write(file_contents.head())
        else:
            st.text(file_contents[:1000] + "...")  # Display first 1000 characters
        
        # Data Cleaning and EDA
        st.subheader("Data Cleaning and EDA")
        
        if isinstance(file_contents, pd.DataFrame):
            # Tabular data
            basic_stats, missing_values, correlation_matrix, df_processed, numeric_columns, categorical_columns = tabular_eda(file_contents)
            
            st.write("Basic Statistics:")
            st.write(basic_stats)
            
            st.write("Missing Values:")
            st.write(missing_values)
            
            st.write("Correlation Matrix:")
            fig = generate_interactive_heatmap(correlation_matrix, "Correlation Matrix")
            st.plotly_chart(fig)
            
            st.write("Processed Data Sample:")
            st.write(df_processed.head())
            
            st.write("Numeric Columns:", numeric_columns.tolist())
            st.write("Categorical Columns:", categorical_columns.tolist())
            
            # Extract context and generate visualizations
            context = extract_context(' '.join(file_contents.columns))
            context_visualizations = generate_context_visualizations(file_contents, context)
            
            for title, fig in context_visualizations:
                st.subheader(title)
                st.plotly_chart(fig)
            
        else:
            # Text data
            cleaned_text = clean_text(file_contents)
            common_words, word_freq_df = text_eda(cleaned_text)
            
            st.write("Most Common Words:")
            st.write(common_words)
            
            st.write("Word Frequency Distribution:")
            fig = generate_interactive_bar_chart(word_freq_df.set_index('Word')['Frequency'].head(20), "Top 20 Words", "Word", "Frequency")
            st.plotly_chart(fig)
            
            # Word Cloud
            st.write("Word Cloud")
            word_cloud = generate_word_cloud(cleaned_text)
            st.pyplot(word_cloud)
            
            # Extract context and insights
            context = extract_context(file_contents)
            st.subheader("Extracted Context")
            for entity, label in context:
                st.write(f"{entity}: {label}")
        
        # Generate visualizations
        st.subheader("General Visualizations")
        
        # Example visualizations for different levels
        # In a real scenario, you'd process the data to extract relevant information for each level
        
        # CEO Level
        st.write("CEO Level - Overall Performance")
        ceo_data = pd.Series({'Revenue': 1000000, 'Profit': 200000, 'Costs': 800000})
        ceo_chart = generate_interactive_pie_chart(ceo_data, "Revenue Breakdown")
        st.plotly_chart(ceo_chart)
        
        # CFO Level
        st.write("CFO Level - Financial Trends")
        cfo_data = pd.Series([100, 120, 110, 140, 130], index=['Jan', 'Feb', 'Mar', 'Apr', 'May'])
        cfo_chart = generate_interactive_line_chart(cfo_data, "Monthly Financial Performance", "Month", "Performance")
        st.plotly_chart(cfo_chart)
        
        # CTO Level
        st.write("CTO Level - Technology Stack Usage")
        cto_data = pd.Series({'Python': 30, 'Java': 25, 'JavaScript': 20, 'C++': 15, 'Others': 10})
        cto_chart = generate_interactive_bar_chart(cto_data, "Technology Stack Distribution", "Technology", "Usage")
        st.plotly_chart(cto_chart)
        
        # CPO Level
        st.write("CPO Level - Product Performance")
        cpo_data = pd.Series({'Product A': 40, 'Product B': 30, 'Product C': 20, 'Product D': 10})
        cpo_chart = generate_interactive_pie_chart(cpo_data, "Product Revenue Share")
        st.plotly_chart(cpo_chart)
        
        # PM Level
        st.write("PM Level - Project Status")
        pm_data = pd.Series({'Completed': 20, 'In Progress': 30, 'Planning': 15, 'On Hold': 5})
        pm_chart = generate_interactive_bar_chart(pm_data, "Project Status Distribution", "Status", "Count")
        st.plotly_chart(pm_chart)

if __name__ == "__main__":
    main()