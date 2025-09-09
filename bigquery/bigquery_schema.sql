-- Google BigQuery Schema for AI-Driven Customer Insights Platform
-- BigQuery DDL Script for Telco Customer Churn Analysis

-- Dataset oluşturma (BigQuery Console'da manuel olarak yapılacak)
-- CREATE SCHEMA IF NOT EXISTS `your-project-id.churn_analysis`;

-- 1. Customer Demographics Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_demographics` (
    customer_id STRING NOT NULL,
    gender STRING NOT NULL,
    senior_citizen BOOL NOT NULL,
    partner BOOL NOT NULL,
    dependents BOOL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY customer_id, gender;

-- 2. Customer Services Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_services` (
    customer_id STRING NOT NULL,
    phone_service BOOL NOT NULL,
    multiple_lines STRING,
    internet_service STRING,
    online_security STRING,
    online_backup STRING,
    device_protection STRING,
    tech_support STRING,
    streaming_tv STRING,
    streaming_movies STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY customer_id, internet_service;

-- 3. Customer Contracts Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_contracts` (
    customer_id STRING NOT NULL,
    tenure_months INT64 NOT NULL,
    contract_type STRING NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY customer_id, contract_type;

-- 4. Customer Billing Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_billing` (
    customer_id STRING NOT NULL,
    monthly_charges FLOAT64 NOT NULL,
    total_charges FLOAT64,
    paperless_billing BOOL NOT NULL,
    payment_method STRING NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY customer_id, payment_method;

-- 5. Customer Churn Table (Main target variable)
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_churn` (
    customer_id STRING NOT NULL,
    churn_status BOOL NOT NULL,
    churn_date DATE,
    churn_reason STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY customer_id, churn_status;

-- 6. Customer Segments Table (for ML clustering results)
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.customer_segments` (
    customer_id STRING NOT NULL,
    segment_id INT64,
    segment_name STRING,
    segment_description STRING,
    cltv_score FLOAT64,
    risk_score FLOAT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY customer_id, segment_id;

-- 7. ML Predictions Table (for storing model predictions)
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.ml_predictions` (
    prediction_id INT64 NOT NULL,
    customer_id STRING NOT NULL,
    model_name STRING NOT NULL,
    model_version STRING NOT NULL,
    prediction_type STRING NOT NULL,
    prediction_value FLOAT64,
    prediction_probability FLOAT64,
    confidence_score FLOAT64,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOL DEFAULT TRUE
)
PARTITION BY DATE(prediction_date)
CLUSTER BY customer_id, model_name;

-- 8. Data Quality Metrics Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.data_quality_metrics` (
    metric_id INT64 NOT NULL,
    table_name STRING NOT NULL,
    metric_name STRING NOT NULL,
    metric_value FLOAT64,
    metric_description STRING,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(check_date)
CLUSTER BY table_name, metric_name;

-- 9. ETL Job Logs Table
CREATE OR REPLACE TABLE `your-project-id.churn_analysis.etl_job_logs` (
    job_id STRING NOT NULL,
    job_name STRING NOT NULL,
    job_status STRING NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_processed INT64,
    error_message STRING,
    job_config STRING
)
PARTITION BY DATE(start_time)
CLUSTER BY job_name, job_status;

-- Views for Analytics

-- Complete Customer View
CREATE OR REPLACE VIEW `your-project-id.churn_analysis.customer_complete_view` AS
SELECT 
    d.customer_id,
    d.gender,
    d.senior_citizen,
    d.partner,
    d.dependents,
    s.phone_service,
    s.multiple_lines,
    s.internet_service,
    s.online_security,
    s.online_backup,
    s.device_protection,
    s.tech_support,
    s.streaming_tv,
    s.streaming_movies,
    c.tenure_months,
    c.contract_type,
    b.monthly_charges,
    b.total_charges,
    b.paperless_billing,
    b.payment_method,
    ch.churn_status,
    ch.churn_date,
    seg.segment_id,
    seg.segment_name,
    seg.cltv_score,
    seg.risk_score,
    d.created_at,
    d.updated_at
FROM `your-project-id.churn_analysis.customer_demographics` d
LEFT JOIN `your-project-id.churn_analysis.customer_services` s ON d.customer_id = s.customer_id
LEFT JOIN `your-project-id.churn_analysis.customer_contracts` c ON d.customer_id = c.customer_id
LEFT JOIN `your-project-id.churn_analysis.customer_billing` b ON d.customer_id = b.customer_id
LEFT JOIN `your-project-id.churn_analysis.customer_churn` ch ON d.customer_id = ch.customer_id
LEFT JOIN `your-project-id.churn_analysis.customer_segments` seg ON d.customer_id = seg.customer_id;

-- Churn Analysis View
CREATE OR REPLACE VIEW `your-project-id.churn_analysis.churn_analysis_view` AS
SELECT 
    contract_type,
    internet_service,
    payment_method,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
    ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate,
    AVG(monthly_charges) as avg_monthly_charges,
    AVG(tenure_months) as avg_tenure_months,
    CURRENT_TIMESTAMP() as analysis_date
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY contract_type, internet_service, payment_method;

-- Customer Lifetime Value Analysis View
CREATE OR REPLACE VIEW `your-project-id.churn_analysis.cltv_analysis_view` AS
SELECT 
    segment_name,
    COUNT(*) as customer_count,
    AVG(cltv_score) as avg_cltv,
    AVG(risk_score) as avg_risk,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_count,
    ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as segment_churn_rate,
    AVG(monthly_charges) as avg_monthly_charges,
    AVG(tenure_months) as avg_tenure_months,
    CURRENT_TIMESTAMP() as analysis_date
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY segment_name;

-- Data Quality Dashboard View
CREATE OR REPLACE VIEW `your-project-id.churn_analysis.data_quality_dashboard` AS
SELECT 
    table_name,
    metric_name,
    metric_value,
    metric_description,
    check_date,
    CASE 
        WHEN metric_name = 'completeness' AND metric_value < 0.95 THEN 'FAIL'
        WHEN metric_name = 'uniqueness' AND metric_value < 0.99 THEN 'FAIL'
        WHEN metric_name = 'validity' AND metric_value < 0.98 THEN 'FAIL'
        ELSE 'PASS'
    END as quality_status
FROM `your-project-id.churn_analysis.data_quality_metrics`
WHERE check_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY check_date DESC, table_name, metric_name;

-- Stored Procedures for Data Quality Checks

-- Procedure to check data completeness
CREATE OR REPLACE PROCEDURE `your-project-id.churn_analysis.check_data_completeness`()
BEGIN
  DECLARE table_name STRING;
  DECLARE completeness_score FLOAT64;
  
  -- Check customer_demographics completeness
  SET table_name = 'customer_demographics';
  SELECT 
    (COUNT(*) - COUNTIF(customer_id IS NULL OR gender IS NULL OR senior_citizen IS NULL)) / COUNT(*) as completeness
  INTO completeness_score
  FROM `your-project-id.churn_analysis.customer_demographics`;
  
  INSERT INTO `your-project-id.churn_analysis.data_quality_metrics`
  (metric_id, table_name, metric_name, metric_value, metric_description)
  VALUES 
  (GENERATE_UUID(), table_name, 'completeness', completeness_score, 'Percentage of non-null values in key columns');
  
  -- Check customer_services completeness
  SET table_name = 'customer_services';
  SELECT 
    (COUNT(*) - COUNTIF(customer_id IS NULL OR phone_service IS NULL)) / COUNT(*) as completeness
  INTO completeness_score
  FROM `your-project-id.churn_analysis.customer_services`;
  
  INSERT INTO `your-project-id.churn_analysis.data_quality_metrics`
  (metric_id, table_name, metric_name, metric_value, metric_description)
  VALUES 
  (GENERATE_UUID(), table_name, 'completeness', completeness_score, 'Percentage of non-null values in key columns');
  
END;

-- Procedure to check data uniqueness
CREATE OR REPLACE PROCEDURE `your-project-id.churn_analysis.check_data_uniqueness`()
BEGIN
  DECLARE table_name STRING;
  DECLARE uniqueness_score FLOAT64;
  
  -- Check customer_demographics uniqueness
  SET table_name = 'customer_demographics';
  SELECT 
    COUNT(DISTINCT customer_id) / COUNT(*) as uniqueness
  INTO uniqueness_score
  FROM `your-project-id.churn_analysis.customer_demographics`;
  
  INSERT INTO `your-project-id.churn_analysis.data_quality_metrics`
  (metric_id, table_name, metric_name, metric_value, metric_description)
  VALUES 
  (GENERATE_UUID(), table_name, 'uniqueness', uniqueness_score, 'Percentage of unique customer_id values');
  
END;

-- Sample Queries for Analytics

-- Query 1: Monthly Churn Trend
/*
SELECT 
  DATE_TRUNC(created_at, MONTH) as month,
  COUNT(*) as total_customers,
  COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
  ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY month
ORDER BY month;
*/

-- Query 2: Customer Segmentation Analysis
/*
SELECT 
  segment_name,
  COUNT(*) as customer_count,
  AVG(cltv_score) as avg_cltv,
  AVG(risk_score) as avg_risk,
  COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_count,
  ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as segment_churn_rate
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY segment_name
ORDER BY avg_cltv DESC;
*/

-- Query 3: Service Usage Impact on Churn
/*
SELECT 
  internet_service,
  streaming_tv,
  streaming_movies,
  COUNT(*) as total_customers,
  COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
  ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate,
  AVG(monthly_charges) as avg_monthly_charges
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY internet_service, streaming_tv, streaming_movies
ORDER BY churn_rate DESC;
*/
