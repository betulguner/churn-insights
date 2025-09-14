"""
Streamlit Web UI for RAG Chatbot
Customer Churn Analysis Chatbot Interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.rag_pipeline import RAGPipeline
from modules.bigquery_client import BigQueryClient

# Page configuration
st.set_page_config(
    page_title="Customer Churn Analysis Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_pipeline():
    """Initialize RAG pipeline with caching"""
    try:
        return RAGPipeline()
    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return None

@st.cache_data
def get_quick_stats():
    """Get quick statistics with caching"""
    try:
        client = BigQueryClient()
        overview = client.get_customer_overview()
        segments = client.get_segment_analysis()
        return overview, segments
    except Exception as e:
        st.error(f"Failed to load statistics: {e}")
        return {}, pd.DataFrame()

def display_stats_dashboard(overview, segments_df):
    """Display statistics dashboard"""
    st.subheader("📊 Customer Overview Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Customers",
            value=f"{overview.get('total_customers', 0):,}",
            delta=None
        )
    
    with col2:
        churn_rate = overview.get('churn_rate', 0)
        st.metric(
            label="Churn Rate",
            value=f"{churn_rate:.1f}%",
            delta=f"-{churn_rate:.1f}%" if churn_rate > 20 else None
        )
    
    with col3:
        st.metric(
            label="Avg Monthly Charges",
            value=f"${overview.get('avg_monthly_charges', 0):.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Avg Tenure",
            value=f"{overview.get('avg_tenure_months', 0):.0f} months",
            delta=None
        )
    
    # Segment analysis
    if not segments_df.empty:
        st.subheader("🎯 Customer Segments Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Churn rate by segment
            fig_churn = px.bar(
                segments_df,
                x='segment_name',
                y='churn_rate',
                title='Churn Rate by Segment',
                color='churn_rate',
                color_continuous_scale='Reds'
            )
            fig_churn.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_churn, use_container_width=True)
        
        with col2:
            # Customer count by segment
            fig_count = px.pie(
                segments_df,
                values='customer_count',
                names='segment_name',
                title='Customer Distribution by Segment'
            )
            st.plotly_chart(fig_count, use_container_width=True)

def display_chat_interface(pipeline):
    """Display chat interface"""
    st.subheader("💬 Ask Questions About Your Customers")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show SQL query if available
            if message["role"] == "assistant" and "sql_query" in message:
                with st.expander("🔍 View SQL Query"):
                    st.code(message["sql_query"], language="sql")
    
    # Chat input
    if prompt := st.chat_input("Ask about customer churn, segments, or trends..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process question with RAG pipeline
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question..."):
                response = pipeline.process_question(prompt)
            
            if response["success"]:
                # Display formatted response
                st.markdown(response["formatted_response"])
                
                # Show results table if available
                if response["results"]:
                    results_df = pd.DataFrame(response["results"])
                    st.dataframe(results_df, use_container_width=True)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["formatted_response"],
                    "sql_query": response["sql_query"]
                })
            else:
                error_msg = f"Sorry, I encountered an error: {response['error']}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

def display_sample_questions():
    """Display sample questions"""
    st.subheader("💡 Sample Questions You Can Ask")
    
    sample_questions = [
        "What's our overall churn rate?",
        "Show me the churn rate by customer segment",
        "Which contract type has the highest churn?",
        "How many high-value customers do we have?",
        "What's the average monthly charges by internet service?",
        "Show me churn trends over time",
        "Which segment has the lowest churn rate?",
        "How many customers are on month-to-month contracts?",
        "What's the average tenure for churned customers?",
        "Show me the top 10 highest value customers"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(f"💬 {question}", key=f"sample_{i}"):
                st.session_state.sample_question = question
                st.rerun()

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🤖 Customer Churn Analysis Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Navigation")
        
        # Check API key
        if not os.getenv('OPENAI_API_KEY'):
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            st.stop()
        
        # Navigation
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Chat Bot", "Sample Questions"]
        )
        
        st.markdown("---")
        st.markdown("### 📋 About")
        st.markdown("""
        This chatbot helps you analyze customer churn data using natural language queries.
        
        **Features:**
        - 📊 Real-time customer statistics
        - 💬 Natural language Q&A
        - 🔍 SQL query generation
        - 📈 Interactive visualizations
        """)
    
    # Initialize RAG pipeline
    pipeline = initialize_rag_pipeline()
    
    if pipeline is None:
        st.error("Failed to initialize the chatbot. Please check your configuration.")
        st.stop()
    
    # Main content based on selected page
    if page == "Dashboard":
        st.header("📊 Customer Analytics Dashboard")
        
        # Load and display statistics
        overview, segments_df = get_quick_stats()
        display_stats_dashboard(overview, segments_df)
        
        # Additional insights
        if not segments_df.empty:
            st.subheader("🔍 Key Insights")
            
            # Find highest and lowest churn segments
            highest_churn_segment = segments_df.loc[segments_df['churn_rate'].idxmax()]
            lowest_churn_segment = segments_df.loc[segments_df['churn_rate'].idxmin()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Highest Churn Segment:** {highest_churn_segment['segment_name']}
                - Churn Rate: {highest_churn_segment['churn_rate']:.1f}%
                - Customer Count: {highest_churn_segment['customer_count']:,}
                """)
            
            with col2:
                st.success(f"""
                **Lowest Churn Segment:** {lowest_churn_segment['segment_name']}
                - Churn Rate: {lowest_churn_segment['churn_rate']:.1f}%
                - Customer Count: {lowest_churn_segment['customer_count']:,}
                """)
    
    elif page == "Chat Bot":
        display_chat_interface(pipeline)
        
        # Handle sample question from sidebar
        if "sample_question" in st.session_state:
            st.session_state.messages.append({
                "role": "user",
                "content": st.session_state.sample_question
            })
            del st.session_state.sample_question
            st.rerun()
    
    elif page == "Sample Questions":
        display_sample_questions()
        
        # Show question categories
        st.subheader("📝 Question Categories")
        
        categories = {
            "Customer Overview": "General customer statistics and demographics",
            "Churn Analysis": "Churn rates, trends, and risk factors",
            "Segment Analysis": "Customer segmentation and segment performance",
            "Revenue Analysis": "Billing, charges, and revenue metrics",
            "Service Analysis": "Service usage and preferences",
            "Trend Analysis": "Time-based trends and patterns"
        }
        
        for category, description in categories.items():
            with st.expander(f"📂 {category}"):
                st.write(description)

if __name__ == "__main__":
    main()
