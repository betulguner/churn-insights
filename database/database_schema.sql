-- AI-Driven Customer Insights Platform Database Schema
-- PostgreSQL DDL Script for Telco Customer Churn Analysis

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS customer_services CASCADE;
DROP TABLE IF EXISTS customer_demographics CASCADE;
DROP TABLE IF EXISTS customer_contracts CASCADE;
DROP TABLE IF EXISTS customer_billing CASCADE;
DROP TABLE IF EXISTS customer_churn CASCADE;
DROP TABLE IF EXISTS customer_segments CASCADE;
DROP TABLE IF EXISTS ml_predictions CASCADE;

-- 1. Customer Demographics Table
CREATE TABLE customer_demographics (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10) NOT NULL,
    senior_citizen BOOLEAN NOT NULL DEFAULT FALSE,
    partner BOOLEAN NOT NULL DEFAULT FALSE,
    dependents BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customer Services Table
CREATE TABLE customer_services (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES customer_demographics(customer_id),
    phone_service BOOLEAN NOT NULL DEFAULT FALSE,
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(20),
    online_backup VARCHAR(20),
    device_protection VARCHAR(20),
    tech_support VARCHAR(20),
    streaming_tv VARCHAR(20),
    streaming_movies VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Customer Contracts Table
CREATE TABLE customer_contracts (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES customer_demographics(customer_id),
    tenure_months INTEGER NOT NULL CHECK (tenure_months >= 0),
    contract_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Customer Billing Table
CREATE TABLE customer_billing (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES customer_demographics(customer_id),
    monthly_charges DECIMAL(10,2) NOT NULL CHECK (monthly_charges >= 0),
    total_charges DECIMAL(12,2),
    paperless_billing BOOLEAN NOT NULL DEFAULT FALSE,
    payment_method VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Customer Churn Table (Main target variable)
CREATE TABLE customer_churn (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES customer_demographics(customer_id),
    churn_status BOOLEAN NOT NULL DEFAULT FALSE,
    churn_date DATE,
    churn_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Customer Segments Table (for ML clustering results)
CREATE TABLE customer_segments (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES customer_demographics(customer_id),
    segment_id INTEGER,
    segment_name VARCHAR(50),
    segment_description TEXT,
    cltv_score DECIMAL(10,2), -- Customer Lifetime Value
    risk_score DECIMAL(5,2), -- Churn risk score (0-100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. ML Predictions Table (for storing model predictions)
CREATE TABLE ml_predictions (
    prediction_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES customer_demographics(customer_id),
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(30) NOT NULL, -- 'churn', 'cltv', 'segment'
    prediction_value DECIMAL(10,4),
    prediction_probability DECIMAL(5,4),
    confidence_score DECIMAL(5,4),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for better performance
CREATE INDEX idx_customer_demographics_gender ON customer_demographics(gender);
CREATE INDEX idx_customer_demographics_senior ON customer_demographics(senior_citizen);
CREATE INDEX idx_customer_contracts_tenure ON customer_contracts(tenure_months);
CREATE INDEX idx_customer_contracts_type ON customer_contracts(contract_type);
CREATE INDEX idx_customer_billing_monthly ON customer_billing(monthly_charges);
CREATE INDEX idx_customer_churn_status ON customer_churn(churn_status);
CREATE INDEX idx_customer_segments_segment ON customer_segments(segment_id);
CREATE INDEX idx_ml_predictions_customer ON ml_predictions(customer_id);
CREATE INDEX idx_ml_predictions_model ON ml_predictions(model_name);
CREATE INDEX idx_ml_predictions_date ON ml_predictions(prediction_date);

-- Create a view for complete customer information
CREATE VIEW customer_complete_view AS
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
    seg.risk_score
FROM customer_demographics d
LEFT JOIN customer_services s ON d.customer_id = s.customer_id
LEFT JOIN customer_contracts c ON d.customer_id = c.customer_id
LEFT JOIN customer_billing b ON d.customer_id = b.customer_id
LEFT JOIN customer_churn ch ON d.customer_id = ch.customer_id
LEFT JOIN customer_segments seg ON d.customer_id = seg.customer_id;

-- Create a view for churn analysis
CREATE VIEW churn_analysis_view AS
SELECT 
    contract_type,
    internet_service,
    payment_method,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
    ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate,
    AVG(monthly_charges) as avg_monthly_charges,
    AVG(tenure_months) as avg_tenure_months
FROM customer_complete_view
GROUP BY contract_type, internet_service, payment_method
ORDER BY churn_rate DESC;

-- Insert sample data validation constraints
ALTER TABLE customer_demographics ADD CONSTRAINT check_gender CHECK (gender IN ('Male', 'Female'));
ALTER TABLE customer_services ADD CONSTRAINT check_multiple_lines CHECK (multiple_lines IN ('Yes', 'No', 'No phone service'));
ALTER TABLE customer_services ADD CONSTRAINT check_internet_service CHECK (internet_service IN ('DSL', 'Fiber optic', 'No'));
ALTER TABLE customer_contracts ADD CONSTRAINT check_contract_type CHECK (contract_type IN ('Month-to-month', 'One year', 'Two year'));
ALTER TABLE customer_billing ADD CONSTRAINT check_payment_method CHECK (payment_method IN ('Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'));

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_customer_demographics_updated_at BEFORE UPDATE ON customer_demographics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_services_updated_at BEFORE UPDATE ON customer_services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_contracts_updated_at BEFORE UPDATE ON customer_contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_billing_updated_at BEFORE UPDATE ON customer_billing FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_churn_updated_at BEFORE UPDATE ON customer_churn FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_segments_updated_at BEFORE UPDATE ON customer_segments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;

COMMENT ON TABLE customer_demographics IS 'Customer demographic information including gender, age, family status';
COMMENT ON TABLE customer_services IS 'Customer service subscriptions and preferences';
COMMENT ON TABLE customer_contracts IS 'Customer contract details and tenure information';
COMMENT ON TABLE customer_billing IS 'Customer billing information and payment methods';
COMMENT ON TABLE customer_churn IS 'Customer churn status and related information';
COMMENT ON TABLE customer_segments IS 'Customer segmentation results from ML models';
COMMENT ON TABLE ml_predictions IS 'Machine learning model predictions and confidence scores';
