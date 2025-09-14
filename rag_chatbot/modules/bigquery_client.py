"""
BigQuery API Client for RAG Chatbot
Handles data queries from BigQuery for natural language processing
"""

import os
import logging
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryClient:
    """BigQuery client for executing SQL queries and retrieving data"""
    
    def __init__(self, project_id: str = None, credentials_path: str = None):
        """
        Initialize BigQuery client
        
        Args:
            project_id: GCP project ID
            credentials_path: Path to service account JSON file
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable is required")
        
        if not self.credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
        
        # Initialize BigQuery client
        self._setup_client()
        
    def _setup_client(self):
        """Setup BigQuery client with credentials"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = bigquery.Client(
                credentials=credentials,
                project=self.project_id
            )
            logger.info(f"BigQuery client initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
            
        Returns:
            pandas.DataFrame: Query results
        """
        try:
            logger.info(f"Executing query: {query[:100]}...")
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert to DataFrame
            df = results.to_dataframe()
            logger.info(f"Query executed successfully. Returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_customer_overview(self) -> Dict[str, Any]:
        """Get customer overview statistics"""
        query = """
        SELECT 
            COUNT(*) as total_customers,
            COUNT(CASE WHEN churn_status = true THEN 1 END) as churned_customers,
            ROUND(COUNT(CASE WHEN churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate,
            ROUND(AVG(cb.monthly_charges), 2) as avg_monthly_charges,
            ROUND(AVG(ct.tenure_months), 2) as avg_tenure_months
        FROM `churn-471614.churn_analysis.customer_churn` cc
        JOIN `churn-471614.churn_analysis.customer_billing` cb ON cc.customer_id = cb.customer_id
        JOIN `churn-471614.churn_analysis.customer_contracts` ct ON cc.customer_id = ct.customer_id
        """
        
        df = self.execute_query(query)
        return df.iloc[0].to_dict()
    
    def get_segment_analysis(self) -> pd.DataFrame:
        """Get customer segment analysis"""
        query = """
        SELECT 
            cs.segment_name,
            COUNT(*) as customer_count,
            COUNT(CASE WHEN cc.churn_status = true THEN 1 END) as churned_customers,
            ROUND(COUNT(CASE WHEN cc.churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate,
            ROUND(AVG(cb.monthly_charges), 2) as avg_monthly_charges,
            ROUND(AVG(ct.tenure_months), 2) as avg_tenure_months
        FROM `churn-471614.churn_analysis.customer_segments` cs
        JOIN `churn-471614.churn_analysis.customer_churn` cc ON cs.customer_id = cc.customer_id
        JOIN `churn-471614.churn_analysis.customer_billing` cb ON cs.customer_id = cb.customer_id
        JOIN `churn-471614.churn_analysis.customer_contracts` ct ON cs.customer_id = ct.customer_id
        GROUP BY cs.segment_name
        ORDER BY churn_rate DESC
        """
        
        return self.execute_query(query)
    
    def get_churn_by_contract_type(self) -> pd.DataFrame:
        """Get churn analysis by contract type"""
        query = """
        SELECT 
            ct.contract_type as contract,
            COUNT(*) as customer_count,
            COUNT(CASE WHEN cc.churn_status = true THEN 1 END) as churned_customers,
            ROUND(COUNT(CASE WHEN cc.churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
        FROM `churn-471614.churn_analysis.customer_churn` cc
        JOIN `churn-471614.churn_analysis.customer_contracts` ct ON cc.customer_id = ct.customer_id
        GROUP BY ct.contract_type
        ORDER BY churn_rate DESC
        """
        
        return self.execute_query(query)
    
    def get_churn_by_internet_service(self) -> pd.DataFrame:
        """Get churn analysis by internet service"""
        query = """
        SELECT 
            cs.internet_service,
            COUNT(*) as customer_count,
            COUNT(CASE WHEN cc.churn_status = true THEN 1 END) as churned_customers,
            ROUND(COUNT(CASE WHEN cc.churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
        FROM `churn-471614.churn_analysis.customer_churn` cc
        JOIN `churn-471614.churn_analysis.customer_services` cs ON cc.customer_id = cs.customer_id
        GROUP BY cs.internet_service
        ORDER BY churn_rate DESC
        """
        
        return self.execute_query(query)
    
    def get_high_value_customers(self, limit: int = 10) -> pd.DataFrame:
        """Get top high-value customers"""
        query = """
        SELECT 
            cc.customer_id,
            cs.segment_name,
            cb.monthly_charges,
            cb.total_charges,
            ct.tenure_months,
            cc.churn_status
        FROM `churn-471614.churn_analysis.customer_churn` cc
        JOIN `churn-471614.churn_analysis.customer_segments` cs ON cc.customer_id = cs.customer_id
        JOIN `churn-471614.churn_analysis.customer_billing` cb ON cc.customer_id = cb.customer_id
        JOIN `churn-471614.churn_analysis.customer_contracts` ct ON cc.customer_id = ct.customer_id
        ORDER BY cb.total_charges DESC
        LIMIT {}
        """.format(limit)
        
        return self.execute_query(query)
    
    def get_churn_trends(self) -> pd.DataFrame:
        """Get churn trends over time"""
        query = """
        SELECT 
            DATE_TRUNC(DATETIME(created_at), MONTH) as month,
            COUNT(*) as total_customers,
            COUNT(CASE WHEN churn_status = true THEN 1 END) as churned_customers,
            ROUND(COUNT(CASE WHEN churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
        FROM `churn-471614.churn_analysis.customer_churn`
        GROUP BY month
        ORDER BY month
        """
        
        return self.execute_query(query)
    
    def search_customers(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Search customers with dynamic filters
        
        Args:
            filters: Dictionary of filter conditions
            
        Returns:
            pandas.DataFrame: Filtered customer data
        """
        base_query = """
        SELECT 
            customer_id,
            gender,
            senior_citizen,
            partner,
            dependents,
            tenure_months,
            phone_service,
            internet_service,
            contract,
            monthly_charges,
            total_charges,
            churn_status,
            segment_name
        FROM `churn-471614.churn_analysis.customer_complete_view`
        WHERE 1=1
        """
        
        # Add dynamic filters
        for key, value in filters.items():
            if key == 'segment_name':
                base_query += f" AND segment_name = '{value}'"
            elif key == 'contract':
                base_query += f" AND contract = '{value}'"
            elif key == 'internet_service':
                base_query += f" AND internet_service = '{value}'"
            elif key == 'churn_status':
                base_query += f" AND churn_status = {value}"
            elif key == 'min_tenure':
                base_query += f" AND tenure_months >= {value}"
            elif key == 'max_tenure':
                base_query += f" AND tenure_months <= {value}"
        
        base_query += " ORDER BY total_charges DESC"
        
        return self.execute_query(base_query)

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize client
        client = BigQueryClient()
        
        # Test basic functionality
        print("Testing BigQuery client...")
        
        # Get customer overview
        overview = client.get_customer_overview()
        print(f"Customer Overview: {overview}")
        
        # Get segment analysis
        segments = client.get_segment_analysis()
        print(f"Segment Analysis:\n{segments}")
        
        # Get churn by contract type
        churn_contract = client.get_churn_by_contract_type()
        print(f"Churn by Contract Type:\n{churn_contract}")
        
        print("BigQuery client test completed successfully!")
        
    except Exception as e:
        print(f"BigQuery client test failed: {e}")
