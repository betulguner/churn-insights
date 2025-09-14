"""
Prompt Templates for RAG Chatbot
Converts natural language questions to SQL queries and formats AI responses
"""

from typing import Dict, Any, List
from langchain.prompts import PromptTemplate

class PromptTemplates:
    """Collection of prompt templates for different RAG tasks"""
    
    def __init__(self):
        self.sql_generation_template = self._create_sql_generation_template()
        self.response_formatting_template = self._create_response_formatting_template()
        self.question_classification_template = self._create_question_classification_template()
    
    def _create_sql_generation_template(self) -> PromptTemplate:
        """Create template for converting natural language to SQL"""
        template = """
You are a SQL expert specializing in customer churn analysis. 
Convert the user's natural language question into a SQL query for BigQuery.

Database Schema:
- customer_complete_view: Main customer data view
- customer_segments: Customer segmentation data
- customer_churn: Churn status and predictions
- customer_billing: Billing and payment information

Available Tables and Key Fields:
1. customer_complete_view:
   - customer_id, gender, senior_citizen, partner, dependents
   - tenure_months, phone_service, internet_service, contract
   - monthly_charges, total_charges, churn_status, segment_name

2. customer_segments:
   - customer_id, segment_name, cltv_score, risk_level

3. customer_churn:
   - customer_id, churn_status, churn_reason, created_at

4. customer_billing:
   - customer_id, monthly_charges, total_charges, payment_method

Common Question Patterns:
- "How many customers churned?" → COUNT with WHERE churn_status = true
- "What's the churn rate by segment?" → GROUP BY segment_name with churn calculation
- "Show me high-value customers" → ORDER BY total_charges DESC
- "Churn trends over time" → GROUP BY DATE_TRUNC(created_at, MONTH)
- "Customers by contract type" → GROUP BY contract

SQL Query Requirements:
1. Use BigQuery syntax (backticks for table names)
2. Use proper aggregations (COUNT, AVG, SUM)
3. Include LIMIT for large result sets
4. Use proper date functions for time-based queries
5. Always include ORDER BY for meaningful results

User Question: {question}

SQL Query:
"""
        
        return PromptTemplate(
            input_variables=["question"],
            template=template
        )
    
    def _create_response_formatting_template(self) -> PromptTemplate:
        """Create template for formatting SQL results into natural language responses"""
        template = """
You are a data analyst providing insights from customer churn analysis.
Format the SQL query results into a clear, actionable business response.

Context:
- This is a customer churn analysis for a telecommunications company
- The data includes customer demographics, services, billing, and churn status
- Focus on actionable insights and business implications

User Question: {question}
SQL Query: {sql_query}
Query Results: {query_results}

Response Guidelines:
1. Start with a direct answer to the user's question
2. Highlight key numbers and percentages
3. Provide business context and implications
4. Suggest actionable recommendations if applicable
5. Use clear, professional language
6. Include specific data points from the results

Formatted Response:
"""
        
        return PromptTemplate(
            input_variables=["question", "sql_query", "query_results"],
            template=template
        )
    
    def _create_question_classification_template(self) -> PromptTemplate:
        """Create template for classifying user questions into categories"""
        template = """
Classify the user's question into one of these categories:

Categories:
1. CUSTOMER_OVERVIEW - General customer statistics and demographics
2. CHURN_ANALYSIS - Churn rates, trends, and risk factors
3. SEGMENT_ANALYSIS - Customer segmentation and segment performance
4. REVENUE_ANALYSIS - Billing, charges, and revenue metrics
5. SERVICE_ANALYSIS - Service usage and preferences
6. PREDICTION_ANALYSIS - ML predictions and risk scoring
7. COMPARISON_ANALYSIS - Comparing different customer groups
8. TREND_ANALYSIS - Time-based trends and patterns
9. SPECIFIC_CUSTOMER - Information about specific customers
10. OTHER - Questions that don't fit other categories

Examples:
- "How many customers do we have?" → CUSTOMER_OVERVIEW
- "What's our churn rate?" → CHURN_ANALYSIS
- "Show me high-value customers" → SEGMENT_ANALYSIS
- "Average monthly charges" → REVENUE_ANALYSIS
- "Internet service preferences" → SERVICE_ANALYSIS
- "Churn predictions" → PREDICTION_ANALYSIS
- "Compare contract types" → COMPARISON_ANALYSIS
- "Monthly churn trends" → TREND_ANALYSIS
- "Customer ID 1234 details" → SPECIFIC_CUSTOMER

User Question: {question}

Category:
"""
        
        return PromptTemplate(
            input_variables=["question"],
            template=template
        )
    
    def get_sql_generation_prompt(self, question: str) -> str:
        """Get formatted prompt for SQL generation"""
        return self.sql_generation_template.format(question=question)
    
    def get_response_formatting_prompt(self, question: str, sql_query: str, query_results: str) -> str:
        """Get formatted prompt for response formatting"""
        return self.response_formatting_template.format(
            question=question,
            sql_query=sql_query,
            query_results=query_results
        )
    
    def get_question_classification_prompt(self, question: str) -> str:
        """Get formatted prompt for question classification"""
        return self.question_classification_template.format(question=question)

# Predefined question patterns for common queries
QUESTION_PATTERNS = {
    "CUSTOMER_OVERVIEW": [
        "How many customers do we have?",
        "What's the total number of customers?",
        "Customer count",
        "Total customers"
    ],
    "CHURN_ANALYSIS": [
        "What's our churn rate?",
        "How many customers churned?",
        "Churn percentage",
        "Customer loss rate"
    ],
    "SEGMENT_ANALYSIS": [
        "Show me high-value customers",
        "Customer segments",
        "Best performing segment",
        "Customer segmentation"
    ],
    "REVENUE_ANALYSIS": [
        "Average monthly charges",
        "Total revenue",
        "Customer billing",
        "Revenue per customer"
    ],
    "SERVICE_ANALYSIS": [
        "Internet service preferences",
        "Most popular services",
        "Service usage",
        "Customer services"
    ],
    "TREND_ANALYSIS": [
        "Churn trends over time",
        "Monthly churn rate",
        "Time-based analysis",
        "Historical trends"
    ]
}

# Example usage
if __name__ == "__main__":
    templates = PromptTemplates()
    
    # Test SQL generation
    question = "What's the churn rate by customer segment?"
    sql_prompt = templates.get_sql_generation_prompt(question)
    print("SQL Generation Prompt:")
    print(sql_prompt)
    print("\n" + "="*50 + "\n")
    
    # Test response formatting
    response_prompt = templates.get_response_formatting_prompt(
        question=question,
        sql_query="SELECT segment_name, churn_rate FROM segments",
        query_results="High Value: 15.2%, Medium Value: 23.1%"
    )
    print("Response Formatting Prompt:")
    print(response_prompt)
    print("\n" + "="*50 + "\n")
    
    # Test question classification
    classification_prompt = templates.get_question_classification_prompt(question)
    print("Question Classification Prompt:")
    print(classification_prompt)
