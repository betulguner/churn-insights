
# Churn Analysis Report

## Executive Summary

- **Total Customers**: 7,043
- **Churned Customers**: 1,869
- **Retained Customers**: 5,174
- **Overall Churn Rate**: 26.54%
- **Retention Rate**: 73.46%

## Key Findings

### 1. Contract Type Analysis

#### Month-to-month
- Customer Count: 3,875
- Churn Rate: 43.0%
- Average Monthly Charges: $66.40
- Average Tenure: 18.0 months

#### One year
- Customer Count: 1,473
- Churn Rate: 11.0%
- Average Monthly Charges: $65.05
- Average Tenure: 42.0 months

#### Two year
- Customer Count: 1,695
- Churn Rate: 3.0%
- Average Monthly Charges: $60.77
- Average Tenure: 56.7 months

### 2. Payment Method Analysis

#### Bank transfer (automatic)
- Customer Count: 1,544
- Churn Rate: 17.0%
- Average Monthly Charges: $67.19
- Average Tenure: 43.7 months

#### Credit card (automatic)
- Customer Count: 1,522
- Churn Rate: 15.0%
- Average Monthly Charges: $66.51
- Average Tenure: 43.3 months

#### Electronic check
- Customer Count: 2,365
- Churn Rate: 45.0%
- Average Monthly Charges: $76.26
- Average Tenure: 25.2 months

#### Mailed check
- Customer Count: 1,612
- Churn Rate: 19.0%
- Average Monthly Charges: $43.92
- Average Tenure: 21.8 months

### 3. Service Analysis

#### Internet_Service
- **DSL**: 2,421 customers, 19.0% churn rate
- **Fiber optic**: 3,096 customers, 42.0% churn rate
- **No**: 1,526 customers, 7.0% churn rate

#### Phone_Service
- **False**: 682 customers, 25.0% churn rate
- **True**: 6,361 customers, 27.0% churn rate

#### Online_Security
- **No**: 3,498 customers, 42.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,019 customers, 15.0% churn rate

#### Online_Backup
- **No**: 3,088 customers, 40.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,429 customers, 22.0% churn rate

#### Device_Protection
- **No**: 3,095 customers, 39.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,422 customers, 23.0% churn rate

#### Tech_Support
- **No**: 3,473 customers, 42.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,044 customers, 15.0% churn rate

#### Streaming_Tv
- **No**: 2,810 customers, 34.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,707 customers, 30.0% churn rate

#### Streaming_Movies
- **No**: 2,785 customers, 34.0% churn rate
- **No internet service**: 1,526 customers, 7.0% churn rate
- **Yes**: 2,732 customers, 30.0% churn rate

### 4. Tenure Analysis

#### 0-12 months
- Customer Count: 2,175
- Churn Rate: 48.0%
- Average Monthly Charges: $56.17

#### 13-24 months
- Customer Count: 1,024
- Churn Rate: 29.0%
- Average Monthly Charges: $61.36

#### 25-36 months
- Customer Count: 832
- Churn Rate: 22.0%
- Average Monthly Charges: $65.58

#### 37-48 months
- Customer Count: 762
- Churn Rate: 19.0%
- Average Monthly Charges: $66.32

#### 49-60 months
- Customer Count: 832
- Churn Rate: 14.0%
- Average Monthly Charges: $70.55

#### 60+ months
- Customer Count: 1,407
- Churn Rate: 7.0%
- Average Monthly Charges: $75.95

### 5. Risk Analysis

#### Low (0-20)
- Customer Count: 1,120
- Churn Rate: 6.0%
- Average Monthly Charges: $64.68
- Average Tenure: 48.4 months

#### Medium-Low (21-40)
- Customer Count: 1,312
- Churn Rate: 14.0%
- Average Monthly Charges: $65.21
- Average Tenure: 35.7 months

#### Medium (41-60)
- Customer Count: 1,831
- Churn Rate: 34.0%
- Average Monthly Charges: $62.57
- Average Tenure: 21.1 months

#### Medium-High (61-80)
- Customer Count: 1,336
- Churn Rate: 57.0%
- Average Monthly Charges: $77.63
- Average Tenure: 17.2 months

#### High (81-100)
- Customer Count: 305
- Churn Rate: 73.0%
- Average Monthly Charges: $90.03
- Average Tenure: 5.0 months

### 6. Correlation Analysis

#### Top Churn Correlations:
- **risk_score**: 0.486
- **tenure_months**: -0.352
- **cltv_score**: -0.199
- **total_charges**: -0.198
- **monthly_charges**: 0.193

## Recommendations

### High Priority Actions:
1. **Focus on Month-to-Month Contracts**: 43.5% churn rate - implement retention programs
2. **Electronic Check Payment**: 45.1% churn rate - offer incentives for automatic payments
3. **Fiber Optic Customers**: 41.9% churn rate - improve service quality and support

### Medium Priority Actions:
1. **New Customers (0-12 months)**: High churn risk - implement onboarding programs
2. **High Monthly Charges**: Monitor and provide value-added services
3. **Senior Citizens**: Higher churn rate - provide specialized support

### Low Priority Actions:
1. **Two-Year Contracts**: Very low churn (2.8%) - maintain current approach
2. **Credit Card Payments**: Low churn (7.2%) - encourage more customers to use this method

## Next Steps

1. **Immediate Actions**:
   - Launch retention campaign for month-to-month customers
   - Implement automatic payment incentives
   - Improve fiber optic service quality

2. **Short-term Actions**:
   - Develop customer onboarding program
   - Create senior citizen support program
   - Analyze high-charge customer satisfaction

3. **Long-term Actions**:
   - Develop predictive churn model
   - Implement real-time churn monitoring
   - Create personalized retention strategies
