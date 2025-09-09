#!/usr/bin/env python3
"""
AI-Driven Customer Insights Platform - ETL Pipeline
Extract, Transform, Load pipeline for Telco Customer Churn data
"""

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChurnETLPipeline:
    """ETL Pipeline for Customer Churn Data"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize ETL Pipeline
        
        Args:
            db_config: Database configuration dictionary
        """
        self.db_config = db_config
        self.engine = None
        self.raw_data = None
        
    def connect_database(self):
        """Establish database connection"""
        try:
            connection_string = (
                f"postgresql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            )
            self.engine = create_engine(connection_string)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def extract_data(self, csv_file_path: str) -> pd.DataFrame:
        """
        Extract data from CSV file
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            Raw pandas DataFrame
        """
        try:
            logger.info(f"Extracting data from {csv_file_path}")
            self.raw_data = pd.read_csv(csv_file_path)
            logger.info(f"Successfully extracted {len(self.raw_data)} records")
            return self.raw_data
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise
    
    def transform_data(self) -> Dict[str, pd.DataFrame]:
        """
        Transform raw data into normalized tables
        
        Returns:
            Dictionary of transformed DataFrames
        """
        if self.raw_data is None:
            raise ValueError("No raw data available. Run extract_data() first.")
        
        logger.info("Starting data transformation")
        
        # Data cleaning and type conversion
        df = self.raw_data.copy()
        
        # Handle missing values in TotalCharges
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'] = df['TotalCharges'].fillna(0)
        
        # Convert boolean columns
        boolean_columns = {
            'SeniorCitizen': lambda x: x == 1,
            'Partner': lambda x: x == 'Yes',
            'Dependents': lambda x: x == 'Yes',
            'PhoneService': lambda x: x == 'Yes',
            'PaperlessBilling': lambda x: x == 'Yes',
            'Churn': lambda x: x == 'Yes'
        }
        
        for col, func in boolean_columns.items():
            df[col] = df[col].apply(func)
        
        # Create transformed tables
        transformed_data = {}
        
        # 1. Customer Demographics
        transformed_data['customer_demographics'] = df[[
            'customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents'
        ]].rename(columns={
            'customerID': 'customer_id',
            'SeniorCitizen': 'senior_citizen',
            'Partner': 'partner',
            'Dependents': 'dependents'
        })
        
        # 2. Customer Services
        transformed_data['customer_services'] = df[[
            'customerID', 'PhoneService', 'MultipleLines', 'InternetService',
            'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
            'StreamingTV', 'StreamingMovies'
        ]].rename(columns={
            'customerID': 'customer_id',
            'PhoneService': 'phone_service',
            'MultipleLines': 'multiple_lines',
            'InternetService': 'internet_service',
            'OnlineSecurity': 'online_security',
            'OnlineBackup': 'online_backup',
            'DeviceProtection': 'device_protection',
            'TechSupport': 'tech_support',
            'StreamingTV': 'streaming_tv',
            'StreamingMovies': 'streaming_movies'
        })
        
        # 3. Customer Contracts
        transformed_data['customer_contracts'] = df[[
            'customerID', 'tenure', 'Contract'
        ]].rename(columns={
            'customerID': 'customer_id',
            'tenure': 'tenure_months',
            'Contract': 'contract_type'
        })
        
        # 4. Customer Billing
        transformed_data['customer_billing'] = df[[
            'customerID', 'MonthlyCharges', 'TotalCharges', 'PaperlessBilling', 'PaymentMethod'
        ]].rename(columns={
            'customerID': 'customer_id',
            'MonthlyCharges': 'monthly_charges',
            'TotalCharges': 'total_charges',
            'PaperlessBilling': 'paperless_billing',
            'PaymentMethod': 'payment_method'
        })
        
        # 5. Customer Churn
        transformed_data['customer_churn'] = df[[
            'customerID', 'Churn'
        ]].rename(columns={
            'customerID': 'customer_id',
            'Churn': 'churn_status'
        })
        
        # Add churn_date for churned customers (simulated)
        churned_mask = transformed_data['customer_churn']['churn_status'] == True
        transformed_data['customer_churn']['churn_date'] = None
        transformed_data['customer_churn'].loc[churned_mask, 'churn_date'] = pd.Timestamp.now().date()
        
        # 6. Customer Segments (initial segmentation based on simple rules)
        segments = self._create_initial_segments(df)
        transformed_data['customer_segments'] = segments
        
        logger.info("Data transformation completed successfully")
        return transformed_data
    
    def _create_initial_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create initial customer segments based on simple business rules
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame with customer segments
        """
        segments = []
        
        for _, row in df.iterrows():
            customer_id = row['customerID']
            
            # Calculate CLTV (Customer Lifetime Value) - simplified
            monthly_charges = row['MonthlyCharges']
            tenure_months = row['tenure']
            cltv = monthly_charges * tenure_months
            
            # Calculate risk score based on churn probability factors
            risk_factors = 0
            
            # Contract type risk
            if row['Contract'] == 'Month-to-month':
                risk_factors += 30
            elif row['Contract'] == 'One year':
                risk_factors += 10
            
            # Payment method risk
            if row['PaymentMethod'] == 'Electronic check':
                risk_factors += 20
            
            # Service usage risk
            if row['InternetService'] == 'Fiber optic' and row['MonthlyCharges'] > 80:
                risk_factors += 15
            
            # Tenure risk
            if tenure_months < 12:
                risk_factors += 25
            
            # Determine segment
            if cltv > 2000 and risk_factors < 20:
                segment_id = 1
                segment_name = "High Value Loyal"
            elif cltv > 1000 and risk_factors < 40:
                segment_id = 2
                segment_name = "Medium Value Stable"
            elif risk_factors > 60:
                segment_id = 3
                segment_name = "High Risk"
            elif tenure_months < 12:
                segment_id = 4
                segment_name = "New Customers"
            else:
                segment_id = 5
                segment_name = "Standard"
            
            segments.append({
                'customer_id': customer_id,
                'segment_id': segment_id,
                'segment_name': segment_name,
                'cltv_score': cltv,
                'risk_score': min(risk_factors, 100)  # Cap at 100
            })
        
        return pd.DataFrame(segments)
    
    def load_data(self, transformed_data: Dict[str, pd.DataFrame]):
        """
        Load transformed data into database tables
        
        Args:
            transformed_data: Dictionary of transformed DataFrames
        """
        if self.engine is None:
            raise ValueError("No database connection. Run connect_database() first.")
        
        logger.info("Starting data loading")
        
        # Define table loading order (respecting foreign key constraints)
        table_order = [
            'customer_demographics',
            'customer_services',
            'customer_contracts',
            'customer_billing',
            'customer_churn',
            'customer_segments'
        ]
        
        for table_name in table_order:
            if table_name in transformed_data:
                try:
                    df = transformed_data[table_name]
                    
                    # Add timestamps
                    df['created_at'] = datetime.now()
                    df['updated_at'] = datetime.now()
                    
                    # Load data
                    df.to_sql(
                        table_name,
                        self.engine,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                    
                    logger.info(f"Successfully loaded {len(df)} records into {table_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load data into {table_name}: {e}")
                    raise
        
        logger.info("Data loading completed successfully")
    
    def validate_data(self) -> Dict[str, Any]:
        """
        Validate loaded data
        
        Returns:
            Dictionary with validation results
        """
        if self.engine is None:
            raise ValueError("No database connection. Run connect_database() first.")
        
        logger.info("Starting data validation")
        
        validation_results = {}
        
        try:
            with self.engine.connect() as conn:
                # Check record counts
                tables = [
                    'customer_demographics', 'customer_services', 'customer_contracts',
                    'customer_billing', 'customer_churn', 'customer_segments'
                ]
                
                for table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    validation_results[table] = count
                    logger.info(f"{table}: {count} records")
                
                # Check data integrity
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_customers,
                        COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
                        ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
                    FROM customer_churn
                """))
                
                churn_stats = result.fetchone()
                validation_results['churn_stats'] = {
                    'total_customers': churn_stats[0],
                    'churned_customers': churn_stats[1],
                    'churn_rate': churn_stats[2]
                }
                
                logger.info(f"Churn rate: {churn_stats[2]}%")
                
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise
        
        logger.info("Data validation completed successfully")
        return validation_results
    
    def run_full_pipeline(self, csv_file_path: str):
        """
        Run the complete ETL pipeline
        
        Args:
            csv_file_path: Path to the CSV file
        """
        logger.info("Starting full ETL pipeline")
        
        try:
            # Extract
            self.extract_data(csv_file_path)
            
            # Transform
            transformed_data = self.transform_data()
            
            # Load
            self.load_data(transformed_data)
            
            # Validate
            validation_results = self.validate_data()
            
            logger.info("ETL pipeline completed successfully")
            return validation_results
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise

def main():
    """Main function to run ETL pipeline"""
    
    # Load environment variables
    load_dotenv()

    # Prefer Docker PG if POSTGRES_PORT set; else fallback to local Homebrew
    db_config = {
        'host': os.getenv('POSTGRES_HOST', os.getenv('LOCAL_PG_HOST', 'localhost')),
        'port': os.getenv('POSTGRES_PORT', os.getenv('LOCAL_PG_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', os.getenv('LOCAL_PG_DB', 'churn_analysis')),
        'user': os.getenv('POSTGRES_USER', os.getenv('LOCAL_PG_USER', 'postgres')),
        'password': os.getenv('POSTGRES_PASSWORD', os.getenv('LOCAL_PG_PASSWORD', '')),
    }
    
    # CSV file path
    csv_file_path = '../WA_Fn-UseC_-Telco-Customer-Churn.csv'
    
    # Initialize and run ETL pipeline
    etl_pipeline = ChurnETLPipeline(db_config)
    
    try:
        etl_pipeline.connect_database()
        validation_results = etl_pipeline.run_full_pipeline(csv_file_path)
        
        print("\n=== ETL PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"Total customers processed: {validation_results['customer_demographics']}")
        print(f"Churn rate: {validation_results['churn_stats']['churn_rate']}%")
        print(f"Churned customers: {validation_results['churn_stats']['churned_customers']}")
        
    except Exception as e:
        logger.error(f"ETL pipeline execution failed: {e}")
        print(f"ETL pipeline failed: {e}")

if __name__ == "__main__":
    main()
