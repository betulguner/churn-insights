"""
AI-Driven Customer Insights Platform - CLTV Analysis Runner
CLTV analizi için ana script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.cltv_analysis import CLTVAnalyzer
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """CLTV analizi ana fonksiyonu"""
    print("🚀 Starting Customer Lifetime Value (CLTV) Analysis...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = CLTVAnalyzer()
    
    # Run CLTV analysis
    print("\n💰 Running CLTV Analysis...")
    cltv_results = analyzer.analyze_cltv()
    
    # Display key findings
    print("\n📈 Key Findings:")
    print("-" * 40)
    
    overall = cltv_results['overall_cltv']
    print(f"Average CLTV: ${overall['avg_cltv']:,.2f}")
    print(f"Median CLTV: ${overall['median_cltv']:,.2f}")
    print(f"Maximum CLTV: ${overall['max_cltv']:,.2f}")
    print(f"Minimum CLTV: ${overall['min_cltv']:,.2f}")
    print(f"Total CLTV: ${overall['total_cltv']:,.2f}")
    
    # Display segment insights
    print("\n🔍 Segment Insights:")
    print("-" * 40)
    
    # Segment analysis
    print("\n👥 Customer Segments:")
    for segment, data in cltv_results['segment_cltv'].items():
        print(f"\n{segment.title()}:")
        for seg_name, seg_data in data.items():
            print(f"  {seg_name}: {seg_data['count']:,} customers, ${seg_data['avg_cltv']:,.2f} avg CLTV, {seg_data['churn_rate']:.1f}% churn rate")
    
    # Risk analysis
    print("\n⚠️ Risk Level Analysis:")
    for risk, data in cltv_results['risk_cltv'].items():
        print(f"  {risk}: {data['count']:,} customers, ${data['avg_cltv']:,.2f} avg CLTV, {data['churn_rate']:.1f}% churn rate")
    
    # Contract analysis
    print("\n📋 Contract Type Analysis:")
    for contract, data in cltv_results['contract_cltv'].items():
        print(f"  {contract}: {data['count']:,} customers, ${data['avg_cltv']:,.2f} avg CLTV, {data['churn_rate']:.1f}% churn rate")
    
    # Service analysis
    print("\n📱 Service Analysis:")
    for service, data in cltv_results['service_cltv'].items():
        print(f"\n{service.title()}:")
        for service_type, service_data in data.items():
            print(f"  {service_type}: {service_data['count']:,} customers, ${service_data['avg_cltv']:,.2f} avg CLTV, {service_data['churn_rate']:.1f}% churn rate")
    
    # CLTV Distribution
    print("\n📊 CLTV Distribution:")
    for cltv_range, data in cltv_results['cltv_distribution'].items():
        print(f"  {cltv_range}: {data['count']:,} customers, {data['churn_rate']:.1f}% churn rate")
    
    # Create visualizations
    print("\n📊 Creating Visualizations...")
    analyzer.visualize_cltv_analysis(cltv_results)
    
    # Generate report
    print("\n📝 Generating Report...")
    analyzer.generate_cltv_report(cltv_results)
    
    print("\n✅ CLTV Analysis Completed!")
    print("=" * 60)
    
    return cltv_results

if __name__ == "__main__":
    results = main()
