#!/usr/bin/env python3
"""
AI-Driven Customer Insights Platform - BigQuery Integration
PostgreSQL to BigQuery data synchronization and management
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.cloud import storage
from sqlalchemy import create_engine
import logging
from datetime import datetime, timedelta
import os
from typing import Dict, Any, List
import json
from dotenv import load_dotenv
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bigquery_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BigQueryIntegration:
    """BigQuery Integration for Customer Churn Data"""
    
    def __init__(self, project_id: str, dataset_id: str, postgres_config: Dict[str, str]):
        """
        Initialize BigQuery Integration
        
        Args:
            project_id: Google Cloud Project ID
            dataset_id: BigQuery Dataset ID
            postgres_config: PostgreSQL configuration
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.postgres_config = postgres_config
        self.bq_client = None
        self.postgres_engine = None
        
    def setup_bigquery_client(self):
        """Setup BigQuery client"""
        try:
            # Prefer explicit service account credentials if provided
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.isfile(cred_path):
                credentials = service_account.Credentials.from_service_account_file(cred_path)
                self.bq_client = bigquery.Client(project=self.project_id, credentials=credentials)
            else:
                # Fallback to default ADC
                self.bq_client = bigquery.Client(project=self.project_id)
            logger.info(f"BigQuery client initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"BigQuery client setup failed: {e}")
            raise
    
    def setup_postgres_connection(self):
        """Setup PostgreSQL connection"""
        try:
            connection_string = (
                f"postgresql://{self.postgres_config['user']}:{self.postgres_config['password']}"
                f"@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
            )
            self.postgres_engine = create_engine(connection_string)
            logger.info("PostgreSQL connection established")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def create_dataset(self):
        """Create BigQuery dataset if it doesn't exist"""
        try:
            dataset_ref = self.bq_client.dataset(self.dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # BigQuery location
            dataset.description = "AI-Driven Customer Insights Platform Dataset"
            
            # Dataset oluştur
            dataset = self.bq_client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset {self.dataset_id} created or already exists")
            
        except Exception as e:
            logger.error(f"Dataset creation failed: {e}")
            raise
    
    def create_tables_from_schema(self, schema_file_path: str):
        """
        Create BigQuery tables from schema file
        
        Args:
            schema_file_path: Path to BigQuery schema SQL file
        """
        try:
            with open(schema_file_path, 'r') as file:
                schema_sql = file.read()
            
            # Project ID'yi değiştir
            schema_sql = schema_sql.replace('your-project-id', self.project_id)
            
            # SQL komutlarını ayır ve çalıştır
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.strip():
                    try:
                        job = self.bq_client.query(statement)
                        job.result()  # Wait for job to complete
                        logger.info(f"Successfully executed: {statement[:50]}...")
                    except Exception as e:
                        logger.warning(f"Statement execution failed: {e}")
                        logger.warning(f"Statement: {statement[:100]}...")
            
            logger.info("BigQuery tables created successfully")
            
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
    
    def sync_table_to_bigquery(self, table_name: str, postgres_table: str):
        """
        Sync a single table from PostgreSQL to BigQuery
        
        Args:
            table_name: BigQuery table name
            postgres_table: PostgreSQL table name
        """
        try:
            logger.info(f"Syncing {postgres_table} to {table_name}")
            
            # PostgreSQL'den veri çek
            query = f"SELECT * FROM {postgres_table}"
            df = pd.read_sql(query, self.postgres_engine)
            
            # BigQuery table reference
            table_ref = self.bq_client.dataset(self.dataset_id).table(table_name)
            
            # Veriyi BigQuery'e yükle
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE",  # Tabloyu temizle ve yeniden yükle
                create_disposition="CREATE_IF_NEEDED"
            )
            
            job = self.bq_client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            
            job.result()  # Wait for job to complete
            
            logger.info(f"Successfully synced {len(df)} records to {table_name}")
            
        except Exception as e:
            logger.error(f"Sync failed for {table_name}: {e}")
            raise
    
    def sync_all_tables(self):
        """Sync all tables from PostgreSQL to BigQuery"""
        try:
            logger.info("Starting full table synchronization")
            
            # Tablo eşleştirmeleri
            table_mappings = {
                'customer_demographics': 'customer_demographics',
                'customer_services': 'customer_services',
                'customer_contracts': 'customer_contracts',
                'customer_billing': 'customer_billing',
                'customer_churn': 'customer_churn',
                'customer_segments': 'customer_segments'
            }
            
            for bq_table, pg_table in table_mappings.items():
                self.sync_table_to_bigquery(bq_table, pg_table)
            
            logger.info("Full table synchronization completed")
            
        except Exception as e:
            logger.error(f"Full synchronization failed: {e}")
            raise
    
    def run_data_quality_checks(self):
        """Run data quality checks in BigQuery"""
        try:
            logger.info("Running data quality checks")
            
            # Completeness check
            completeness_query = f"""
            SELECT 
                'customer_demographics' as table_name,
                'completeness' as metric_name,
                (COUNT(*) - COUNTIF(customer_id IS NULL OR gender IS NULL)) / COUNT(*) as metric_value,
                'Percentage of non-null values in key columns' as metric_description,
                CURRENT_TIMESTAMP() as check_date
            FROM `{self.project_id}.{self.dataset_id}.customer_demographics`
            """
            
            job = self.bq_client.query(completeness_query)
            result = job.result()
            
            for row in result:
                logger.info(f"Data quality check result: {row.table_name} - {row.metric_name}: {row.metric_value}")
            
            logger.info("Data quality checks completed")
            
        except Exception as e:
            logger.error(f"Data quality checks failed: {e}")
            raise
    
    def create_sample_analytics_queries(self):
        """Create and run sample analytics queries"""
        try:
            logger.info("Running sample analytics queries")
            
            # Churn rate analysis
            churn_query = f"""
            SELECT 
                contract_type,
                internet_service,
                COUNT(*) as total_customers,
                COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
                ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
            FROM `{self.project_id}.{self.dataset_id}.customer_complete_view`
            GROUP BY contract_type, internet_service
            ORDER BY churn_rate DESC
            LIMIT 10
            """
            
            job = self.bq_client.query(churn_query)
            result = job.result()
            
            logger.info("Churn Rate Analysis Results:")
            for row in result:
                logger.info(f"{row.contract_type} + {row.internet_service}: {row.churn_rate}% churn rate")
            
            # Customer segmentation analysis
            segment_query = f"""
            SELECT 
                segment_name,
                COUNT(*) as customer_count,
                ROUND(AVG(cltv_score), 2) as avg_cltv,
                ROUND(AVG(risk_score), 2) as avg_risk,
                COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_count
            FROM `{self.project_id}.{self.dataset_id}.customer_complete_view`
            GROUP BY segment_name
            ORDER BY avg_cltv DESC
            """
            
            job = self.bq_client.query(segment_query)
            result = job.result()
            
            logger.info("Customer Segmentation Analysis Results:")
            for row in result:
                logger.info(f"{row.segment_name}: {row.customer_count} customers, CLTV: {row.avg_cltv}")
            
            logger.info("Sample analytics queries completed")
            
        except Exception as e:
            logger.error(f"Analytics queries failed: {e}")
            raise
    
    def setup_automated_sync(self):
        """Setup automated synchronization (for future use)"""
        try:
            logger.info("Setting up automated sync configuration")
            
            # ETL job log entry
            job_log = {
                'job_id': f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'job_name': 'postgres_to_bigquery_sync',
                'job_status': 'completed',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'records_processed': 7043,  # Total records
                'error_message': None,
                'job_config': json.dumps({
                    'source': 'postgresql',
                    'destination': 'bigquery',
                    'tables': ['customer_demographics', 'customer_services', 'customer_contracts', 
                              'customer_billing', 'customer_churn', 'customer_segments']
                })
            }
            
            logger.info(f"ETL job logged: {job_log['job_id']}")
            
        except Exception as e:
            logger.error(f"Automated sync setup failed: {e}")
            raise
    
    def run_full_integration(self, schema_file_path: str):
        """
        Run full BigQuery integration
        
        Args:
            schema_file_path: Path to BigQuery schema SQL file
        """
        try:
            logger.info("Starting full BigQuery integration")
            
            # Setup clients
            self.setup_bigquery_client()
            self.setup_postgres_connection()
            
            # Create dataset
            self.create_dataset()
            
            # Create tables from schema
            self.create_tables_from_schema(schema_file_path)
            
            # Sync all tables
            self.sync_all_tables()
            
            # Run data quality checks
            self.run_data_quality_checks()
            
            # Run sample analytics
            self.create_sample_analytics_queries()
            
            # Setup automated sync
            self.setup_automated_sync()
            
            logger.info("Full BigQuery integration completed successfully")
            
        except Exception as e:
            logger.error(f"Full integration failed: {e}")
            raise

def main():
    """Main function to run BigQuery integration"""
    
    # Load env
    load_dotenv()

    # Configuration
    project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
    dataset_id = "churn_analysis"
    
    postgres_config = {
        'host': os.getenv('POSTGRES_HOST', os.getenv('LOCAL_PG_HOST', 'localhost')),
        'port': os.getenv('POSTGRES_PORT', os.getenv('LOCAL_PG_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', os.getenv('LOCAL_PG_DB', 'churn_analysis')),
        'user': os.getenv('POSTGRES_USER', os.getenv('LOCAL_PG_USER', 'postgres')),
        'password': os.getenv('POSTGRES_PASSWORD', os.getenv('LOCAL_PG_PASSWORD', '')),
    }
    
    schema_file_path = 'bigquery/bigquery_schema.sql'
    
    # Initialize and run BigQuery integration
    bq_integration = BigQueryIntegration(project_id, dataset_id, postgres_config)
    
    try:
        print("\n=== BIGQUERY INTEGRATION START ===")
        print("Project:", project_id)
        print("Dataset:", dataset_id)
        print("Postgres host:", postgres_config['host'], "port:", postgres_config['port'])
        print("Credentials:", os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '<not set>'))
        
        # Run full integration: create tables/views, sync data, run checks and sample analytics
        bq_integration.run_full_integration(schema_file_path)
        
    except Exception as e:
        logger.error(f"BigQuery integration setup failed: {e}")
        print(f"BigQuery integration failed: {e}")

if __name__ == "__main__":
    main()
