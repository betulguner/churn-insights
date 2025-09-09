#!/usr/bin/env python3

from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()
gcp_project_id = os.getenv('GCP_PROJECT_ID')
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=gcp_project_id)

# Check data in BigQuery
query = """
SELECT 
  COUNT(*) as total_customers,
  COUNT(CASE WHEN churn_status = true THEN 1 END) as churned_customers,
  ROUND(COUNT(CASE WHEN churn_status = true THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM `churn-471614.churn_analysis.customer_churn`
"""

result = client.query(query).to_dataframe()
print('BigQuery Data Summary:')
print(result)

# Check some sample data
sample_query = """
SELECT customer_id, churn_status, churn_date, churn_reason
FROM `churn-471614.churn_analysis.customer_churn`
WHERE churn_status = true
LIMIT 5
"""

sample_result = client.query(sample_query).to_dataframe()
print('\nSample Churned Customers:')
print(sample_result)
