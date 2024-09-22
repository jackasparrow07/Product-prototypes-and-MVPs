import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def export_report(df, eda_results, advanced_viz_results, ml_results):
    st.header("6. Export Options")
    
    export_format = st.selectbox("Choose export format:", (".md", ".csv", ".png", ".svg", ".txt"))
    
    if st.button("Generate and Download Report"):
        if export_format == ".md":
            markdown_report = generate_markdown_report(df, eda_results, advanced_viz_results, ml_results)
            download_report(markdown_report, "report.md", "text/markdown")
        elif export_format == ".csv":
            csv_report = df.to_csv(index=False)
            download_report(csv_report, "data.csv", "text/csv")
        elif export_format in (".png", ".svg"):
            img = generate_summary_plot(df, eda_results, ml_results)
            download_report(img, f"summary_plot{export_format}", f"image/{export_format[1:]}")
        else:  # .txt
            text_report = generate_text_report(df, eda_results, advanced_viz_results, ml_results)
            download_report(text_report, "report.txt", "text/plain")
        
        st.success("Report generated and ready for download!")

def generate_markdown_report(df, eda_results, advanced_viz_results, ml_results):
    markdown_report = f"""
    # Data Analysis Report

    ## Dataset Overview
    - Number of rows: {df.shape[0]}
    - Number of columns: {df.shape[1]}

    ## Summary Statistics
    {df.describe(include='all').to_markdown()}

    ## Correlation Matrix
    {eda_results['correlation_matrix'].to_markdown() if eda_results['correlation_matrix'] is not None else "No correlation matrix available."}

    ## Advanced Visualizations
    - Scatter Plot: {advanced_viz_results['scatter_plot']}
    - Time Series: {advanced_viz_results['time_series']}
    - Pair Plot: {advanced_viz_results['pair_plot']}
    - 3D Scatter Plot: {advanced_viz_results['3d_scatter']}

    ## Machine Learning Results
    - Target Column: {ml_results['target_column']}
    - Model Performance: {ml_results['model_performance']}

    ### Feature Importance
    {pd.DataFrame(ml_results['feature_importance']).to_markdown()}
    """
    return markdown_report

def generate_text_report(df, eda_results, advanced_viz_results, ml_results):
    text_report = f"""
    Dataset Summary:
    Number of rows: {df.shape[0]}
    Number of columns: {df.shape[1]}
    
    Column Information:
    {df.dtypes.to_string()}
    
    Summary Statistics:
    {df.describe(include='all').to_string()}
    
    Advanced Visualizations:
    - Scatter Plot: {advanced_viz_results['scatter_plot']}
    - Time Series: {advanced_viz_results['time_series']}
    - Pair Plot: {advanced_viz_results['pair_plot']}
    - 3D Scatter Plot: {advanced_viz_results['3d_scatter']}
    
    Machine Learning Results:
    - Target Column: {ml_results['target_column']}
    - Model Performance: {ml_results['model_performance']}
    
    Feature Importance:
    {pd.DataFrame(ml_results['feature_importance']).to_string()}
    """
    return text_report

def generate_summary_plot(df, eda_results, ml_results):
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    
    # Histograms
    df.select_dtypes(include=[np.number]).hist(ax=axs[0, 0])
    axs[0, 0].set_title("Histograms")
    
    # Correlation Matrix
    if eda_results['correlation_matrix'] is not None:
        sns.heatmap(eda_results['correlation_matrix'], annot=True, cmap='coolwarm', ax=axs[0, 1])
        axs[0, 1].set_title("Correlation Matrix")
    
    # Feature Importance
    feature_importance = pd.DataFrame(ml_results['feature_importance'])
    feature_importance.plot(kind='bar', x='feature', y='importance', ax=axs[1, 0])
    axs[1, 0].set_title("Feature Importance")
    
    # Box Plots
    df.select_dtypes(include=[np.number]).boxplot(ax=axs[1, 1])
    axs[1, 1].set_title("Box Plots")
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return img.getvalue()

def download_report(content, filename, mime_type):
    b64 = base64.b64encode(content.encode()).decode() if isinstance(content, str) else base64.b64encode(content).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    st.markdown(href, unsafe_allow_html=True)