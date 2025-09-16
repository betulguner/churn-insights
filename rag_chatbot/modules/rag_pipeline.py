"""
RAG Pipeline for Customer Churn Analysis Chatbot
Combines SQL generation, BigQuery execution, and AI response formatting
"""

import os
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import ollama

from .bigquery_client import BigQueryClient
from .prompt_templates import PromptTemplates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG Pipeline for processing natural language questions about customer churn"""
    
    def __init__(self, openai_api_key: str = None, use_ollama: bool = False):
        """
        Initialize RAG Pipeline
        
        Args:
            openai_api_key: OpenAI API key (optional, can use environment variable)
            use_ollama: If True, use Ollama instead of OpenAI
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.use_ollama = use_ollama
        
        # Initialize components
        self.bigquery_client = BigQueryClient()
        self.prompt_templates = PromptTemplates()
        
        if self.use_ollama:
            self.llm = None  # Ollama doesn't use LangChain ChatOpenAI
            logger.info("RAG Pipeline initialized with Ollama")
        else:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
            
            self.llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.1,  # Low temperature for consistent SQL generation
                max_tokens=1000
            )
            logger.info("RAG Pipeline initialized with OpenAI")
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call Ollama model
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            
        Returns:
            str: Model response
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model="llama3.1:8b",
                messages=messages,
                options={
                    "temperature": 0.1,
                    "num_predict": 1000
                }
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise
    
    def classify_question(self, question: str) -> str:
        """
        Classify user question into a category
        
        Args:
            question: User's natural language question
            
        Returns:
            str: Question category
        """
        try:
            if self.use_ollama:
                prompt = self.prompt_templates.get_question_classification_prompt(question)
                system_prompt = "You are a question classification expert. Return only the category name."
                category = self._call_ollama(prompt, system_prompt)
            else:
                prompt = self.prompt_templates.get_question_classification_prompt(question)
                
                messages = [
                    SystemMessage(content="You are a question classification expert. Return only the category name."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                category = response.content.strip()
            
            logger.info(f"Question classified as: {category}")
            return category
            
        except Exception as e:
            logger.error(f"Question classification failed: {e}")
            return "OTHER"
    
    def generate_sql_query(self, question: str) -> str:
        """
        Generate SQL query from natural language question
        
        Args:
            question: User's natural language question
            
        Returns:
            str: Generated SQL query
        """
        try:
            if self.use_ollama:
                prompt = self.prompt_templates.get_sql_generation_prompt(question)
                system_prompt = "You are a SQL expert. Return only the SQL query without any explanations."
                sql_query = self._call_ollama(prompt, system_prompt)
            else:
                prompt = self.prompt_templates.get_sql_generation_prompt(question)
                
                messages = [
                    SystemMessage(content="You are a SQL expert. Return only the SQL query without any explanations."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                sql_query = response.content.strip()
            
            # Clean up the SQL query (remove markdown formatting if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query using BigQuery client
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            pandas.DataFrame: Query results
        """
        try:
            results = self.bigquery_client.execute_query(sql_query)
            logger.info(f"Query executed successfully. Returned {len(results)} rows")
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def format_response(self, question: str, sql_query: str, query_results: pd.DataFrame) -> str:
        """
        Format query results into natural language response
        
        Args:
            question: Original user question
            sql_query: SQL query that was executed
            query_results: Results from BigQuery
            
        Returns:
            str: Formatted natural language response
        """
        try:
            # Convert DataFrame to string representation
            results_str = query_results.to_string(index=False)
            
            prompt = self.prompt_templates.get_response_formatting_prompt(
                question=question,
                sql_query=sql_query,
                query_results=results_str
            )
            
            if self.use_ollama:
                system_prompt = "You are a data analyst providing business insights. Be concise and actionable."
                formatted_response = self._call_ollama(prompt, system_prompt)
            else:
                messages = [
                    SystemMessage(content="You are a data analyst providing business insights. Be concise and actionable."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                formatted_response = response.content.strip()
            
            logger.info("Response formatted successfully")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            # Fallback to simple results display
            return f"Query executed successfully. Results:\n{query_results.to_string(index=False)}"
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question through the complete RAG pipeline
        
        Args:
            question: User's natural language question
            
        Returns:
            Dict containing the complete response with metadata
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Step 1: Classify question
            category = self.classify_question(question)
            
            # Step 2: Generate SQL query
            sql_query = self.generate_sql_query(question)
            
            # Step 3: Execute query
            query_results = self.execute_query(sql_query)
            
            # Step 4: Format response
            formatted_response = self.format_response(question, sql_query, query_results)
            
            # Prepare response
            response = {
                "question": question,
                "category": category,
                "sql_query": sql_query,
                "results": query_results.to_dict('records') if not query_results.empty else [],
                "formatted_response": formatted_response,
                "success": True,
                "error": None
            }
            
            logger.info("Question processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Question processing failed: {e}")
            return {
                "question": question,
                "category": "ERROR",
                "sql_query": None,
                "results": [],
                "formatted_response": f"Sorry, I encountered an error processing your question: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick customer statistics for dashboard"""
        try:
            overview = self.bigquery_client.get_customer_overview()
            segments = self.bigquery_client.get_segment_analysis()
            
            return {
                "overview": overview,
                "segments": segments.to_dict('records') if not segments.empty else [],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Quick stats retrieval failed: {e}")
            return {
                "overview": {},
                "segments": [],
                "success": False,
                "error": str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize RAG pipeline
        pipeline = RAGPipeline()
        
        # Test questions
        test_questions = [
            "What's our overall churn rate?",
            "Show me the churn rate by customer segment",
            "Which contract type has the highest churn?",
            "How many high-value customers do we have?"
        ]
        
        print("Testing RAG Pipeline...")
        print("="*50)
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            response = pipeline.process_question(question)
            
            if response["success"]:
                print(f"Category: {response['category']}")
                print(f"SQL: {response['sql_query']}")
                print(f"Response: {response['formatted_response']}")
            else:
                print(f"Error: {response['error']}")
            
            print("-" * 30)
        
        # Test quick stats
        print("\nTesting Quick Stats...")
        stats = pipeline.get_quick_stats()
        if stats["success"]:
            print(f"Overview: {stats['overview']}")
            print(f"Segments: {len(stats['segments'])} segments found")
        else:
            print(f"Error: {stats['error']}")
        
        print("\nRAG Pipeline test completed!")
        
    except Exception as e:
        print(f"RAG Pipeline test failed: {e}")
