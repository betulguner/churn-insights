"""
AI-Driven Customer Insights Platform - Churn Prediction Runner
Churn prediction modellerini çalıştırmak için ana script
"""

import sys
import os

# Add the parent directory to the Python path to allow importing from 'analytics'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analytics.churn_prediction import ChurnPredictor

def main():
    print("🚀 Starting Churn Prediction Analysis...")
    print("=" * 60)
    
    predictor = ChurnPredictor()
    print("✅ Database connection established")
    
    print("\n🤖 Running Churn Prediction Models...")
    results = predictor.run_churn_prediction()
    
    print("\n✅ Churn Prediction Analysis Completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
