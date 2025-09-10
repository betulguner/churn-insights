"""
AI-Driven Customer Insights Platform - Churn Analysis Runner
Churn oranı analizi için ana script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.churn_analysis import ChurnAnalyzer
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """Churn analizi ana fonksiyonu"""
    print("🚀 Starting Customer Churn Analysis...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ChurnAnalyzer()
    
    # Run churn analysis
    print("\n📊 Running Churn Analysis...")
    churn_results = analyzer.analyze_churn_factors()
    
    # Display key findings
    print("\n📈 Key Findings:")
    print("-" * 40)
    
    overall = churn_results['overall_churn']
    print(f"Total Customers: {overall['total_customers']:,}")
    print(f"Churned Customers: {overall['churned_customers']:,}")
    print(f"Retained Customers: {overall['retained_customers']:,}")
    print(f"Overall Churn Rate: {overall['churn_rate']}%")
    print(f"Retention Rate: {overall['retention_rate']}%")
    
    # Display critical churn factors
    print("\n🔍 Critical Churn Factors:")
    print("-" * 40)
    
    # Contract analysis
    print("\n📋 Contract Type Analysis:")
    for contract, data in churn_results['contract_analysis'].items():
        print(f"  {contract}: {data['churn_rate']:.1f}% churn rate ({data['count']:,} customers)")
    
    # Payment analysis
    print("\n💳 Payment Method Analysis:")
    for payment, data in churn_results['payment_analysis'].items():
        print(f"  {payment}: {data['churn_rate']:.1f}% churn rate ({data['count']:,} customers)")
    
    # Service analysis
    print("\n📱 Internet Service Analysis:")
    internet_data = churn_results['service_analysis']['internet_service']
    for service, data in internet_data.items():
        print(f"  {service}: {data['churn_rate']:.1f}% churn rate ({data['count']:,} customers)")
    
    # Tenure analysis
    print("\n⏰ Tenure Analysis:")
    for tenure, data in churn_results['tenure_analysis'].items():
        print(f"  {tenure} months: {data['churn_rate']:.1f}% churn rate ({data['count']:,} customers)")
    
    # Risk analysis
    print("\n⚠️ Risk Level Analysis:")
    for risk, data in churn_results['risk_analysis'].items():
        print(f"  {risk}: {data['churn_rate']:.1f}% churn rate ({data['count']:,} customers)")
    
    # Correlation analysis
    print("\n🔗 Top Churn Correlations:")
    correlations = churn_results['correlation_analysis']['churn_correlations']
    for factor, correlation in list(correlations.items())[:5]:
        print(f"  {factor}: {correlation:.3f}")
    
    # Create visualizations
    print("\n📊 Creating Visualizations...")
    analyzer.visualize_churn_analysis(churn_results)
    
    # Generate report
    print("\n📝 Generating Report...")
    analyzer.generate_churn_report(churn_results)
    
    print("\n✅ Churn Analysis Completed!")
    print("=" * 60)
    
    return churn_results

if __name__ == "__main__":
    results = main()
