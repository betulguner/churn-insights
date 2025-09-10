"""
AI-Driven Customer Insights Platform - Segment Analysis
Segment analizi için ana script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.data_analyzer import DataAnalyzer
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """Segment analizi ana fonksiyonu"""
    print("🚀 Starting Customer Segment Analysis...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DataAnalyzer()
    
    # Run segment analysis
    print("\n📊 Running Segment Analysis...")
    segment_results = analyzer.segment_analysis()
    
    # Display key findings
    print("\n📈 Key Findings:")
    print("-" * 40)
    
    summary = segment_results['overall_summary']
    print(f"Total Customers: {summary['total_customers']:,}")
    print(f"Churned Customers: {summary['total_churned']:,}")
    print(f"Overall Churn Rate: {summary['overall_churn_rate']}%")
    print(f"Average Monthly Charges: ${summary['avg_monthly_charges']:,.2f}")
    print(f"Average Total Charges: ${summary['avg_total_charges']:,.2f}")
    print(f"Average Tenure: {summary['avg_tenure_months']:.1f} months")
    
    # Display segment insights
    print("\n🔍 Segment Insights:")
    print("-" * 40)
    
    # Demographics
    print("\n👥 Demographics:")
    for col, data in segment_results['demographic_segments'].items():
        print(f"\n{col.title()}:")
        for idx, row in data.iterrows():
            print(f"  {idx}: {row['count']:,} customers, {row['churn_rate']:.1f}% churn rate")
    
    # Services
    print("\n📱 Services:")
    for col, data in segment_results['service_segments'].items():
        print(f"\n{col.title()}:")
        for idx, row in data.iterrows():
            print(f"  {idx}: {row['count']:,} customers, {row['churn_rate']:.1f}% churn rate")
    
    # Contracts
    print("\n📋 Contracts:")
    for col, data in segment_results['contract_segments'].items():
        print(f"\n{col.title()}:")
        for idx, row in data.iterrows():
            print(f"  {idx}: {row['count']:,} customers, {row['churn_rate']:.1f}% churn rate")
    
    # Risk
    print("\n⚠️ Risk Levels:")
    for col, data in segment_results['risk_segments'].items():
        print(f"\n{col.title()}:")
        for idx, row in data.iterrows():
            print(f"  {idx}: {row['count']:,} customers, {row['churn_rate']:.1f}% churn rate")
    
    # Create visualizations
    print("\n📊 Creating Visualizations...")
    analyzer.visualize_segments(segment_results)
    
    # Generate report
    print("\n📝 Generating Report...")
    analyzer.generate_report(segment_results)
    
    print("\n✅ Segment Analysis Completed!")
    print("=" * 60)
    
    return segment_results

if __name__ == "__main__":
    results = main()
