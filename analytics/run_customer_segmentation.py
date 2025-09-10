"""
AI-Driven Customer Insights Platform - Customer Segmentation Runner
Customer segmentation modellerini çalıştırmak için ana script
"""

import sys
import os

# Add the parent directory to the Python path to allow importing from 'analytics'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analytics.customer_segmentation import CustomerSegmenter

def main():
    print("🚀 Starting Customer Segmentation Analysis...")
    print("=" * 60)
    
    segmenter = CustomerSegmenter()
    print("✅ Database connection established")
    
    print("\n🎯 Running Customer Segmentation...")
    results = segmenter.run_customer_segmentation()
    
    print("\n✅ Customer Segmentation Analysis Completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
