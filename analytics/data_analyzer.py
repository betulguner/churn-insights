"""
AI-Driven Customer Insights Platform - Data Analyzer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
from typing import Dict, List, Tuple, Optional
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DataAnalyzer:    
    def __init__(self, config: Optional[Dict] = None):

        load_dotenv()
        
        if config:
            self.config = config
        else:
            # Default PostgreSQL config
            self.config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5433)),
                'database': os.getenv('POSTGRES_DB', 'churn_analysis'),
                'user': os.getenv('POSTGRES_USER', 'churn_user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'churn_password')
            }
        
        # Database connection
        self.engine = self._create_connection()
        
        # Analysis results storage
        self.results = {}
        
    def _create_connection(self):
        """Veritabanı bağlantısı oluştur"""
        try:
            connection_string = (
                f"postgresql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ Database connection established")
            return engine
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def load_data(self, query: str) -> pd.DataFrame:
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            print(f"✅ Data loaded: {len(df)} records")
            return df
        except Exception as e:
            print(f"❌ Data loading failed: {e}")
            raise
    
    def segment_analysis(self, 
                        demographic_cols: List[str] = None,
                        service_cols: List[str] = None,
                        contract_cols: List[str] = None,
                        risk_cols: List[str] = None) -> Dict:
        """
        Segment analizi yap
        
            demographic_cols: Demografik kolonlar
            service_cols: Hizmet kolonları
            contract_cols: Sözleşme kolonları
            risk_cols: Risk kolonları

            Segment analizi sonuçları
        """
        print("🔍 Starting Segment Analysis...")
        
        # Default columns if not provided
        if demographic_cols is None:
            demographic_cols = ['gender', 'senior_citizen', 'partner', 'dependents']
        
        if service_cols is None:
            service_cols = ['internet_service', 'phone_service', 'multiple_lines', 
                          'online_security', 'online_backup', 'device_protection', 
                          'tech_support', 'streaming_tv', 'streaming_movies']
        
        if contract_cols is None:
            contract_cols = ['contract_type', 'payment_method']
        
        if risk_cols is None:
            risk_cols = ['risk_score']
        
        # Load complete customer data
        query = """
        SELECT * FROM customer_complete_view
        """
        
        df = self.load_data(query)
        
        # Segment analysis results
        segment_results = {
            'demographic_segments': self._analyze_demographic_segments(df, demographic_cols),
            'service_segments': self._analyze_service_segments(df, service_cols),
            'contract_segments': self._analyze_contract_segments(df, contract_cols),
            'risk_segments': self._analyze_risk_segments(df, risk_cols),
            'overall_summary': self._create_segment_summary(df)
        }
        
        self.results['segment_analysis'] = segment_results
        print("✅ Segment Analysis completed")
        
        return segment_results
    
    def _analyze_demographic_segments(self, df: pd.DataFrame, cols: List[str]) -> Dict:
        """Demografik segment analizi"""
        results = {}
        
        for col in cols:
            if col in df.columns:
                segment_stats = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean',
                    'tenure_months': 'mean'
                }).round(2)
                
                segment_stats.columns = ['count', 'churned_count', 'churn_rate', 
                                       'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
                
                results[col] = segment_stats
                
        return results
    
    def _analyze_service_segments(self, df: pd.DataFrame, cols: List[str]) -> Dict:
        """Hizmet segment analizi"""
        results = {}
        
        for col in cols:
            if col in df.columns:
                segment_stats = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean'
                }).round(2)
                
                segment_stats.columns = ['count', 'churned_count', 'churn_rate', 
                                       'avg_monthly_charges', 'avg_total_charges']
                
                results[col] = segment_stats
                
        return results
    
    def _analyze_contract_segments(self, df: pd.DataFrame, cols: List[str]) -> Dict:
        """Sözleşme segment analizi"""
        results = {}
        
        for col in cols:
            if col in df.columns:
                segment_stats = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean',
                    'tenure_months': 'mean'
                }).round(2)
                
                segment_stats.columns = ['count', 'churned_count', 'churn_rate', 
                                       'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
                
                results[col] = segment_stats
                
        return results
    
    def _analyze_risk_segments(self, df: pd.DataFrame, cols: List[str]) -> Dict:
        """Risk segment analizi"""
        results = {}
        
        for col in cols:
            if col in df.columns:
                segment_stats = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean',
                    'tenure_months': 'mean'
                }).round(2)
                
                segment_stats.columns = ['count', 'churned_count', 'churn_rate', 
                                       'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
                
                results[col] = segment_stats
                
        return results
    
    def _create_segment_summary(self, df: pd.DataFrame) -> Dict:
        """Genel segment özeti"""
        total_customers = len(df)
        total_churned = df['churn_status'].sum()
        overall_churn_rate = (total_churned / total_customers) * 100
        
        summary = {
            'total_customers': total_customers,
            'total_churned': total_churned,
            'overall_churn_rate': round(overall_churn_rate, 2),
            'avg_monthly_charges': round(df['monthly_charges'].mean(), 2),
            'avg_total_charges': round(df['total_charges'].mean(), 2),
            'avg_tenure_months': round(df['tenure_months'].mean(), 2)
        }
        
        return summary
    
    def visualize_segments(self, segment_results: Dict, save_path: str = "analytics/plots/"):
        """
        Segment analizi görselleştirmeleri

            segment_results: Segment analizi sonuçları
            save_path: Grafiklerin kaydedileceği yol
        """
        print("📊 Creating segment visualizations...")
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # 1. Overall Summary
        self._plot_overall_summary(segment_results['overall_summary'], save_path)
        
        # 2. Demographic Segments
        self._plot_demographic_segments(segment_results['demographic_segments'], save_path)
        
        # 3. Service Segments
        self._plot_service_segments(segment_results['service_segments'], save_path)
        
        # 4. Contract Segments
        self._plot_contract_segments(segment_results['contract_segments'], save_path)
        
        # 5. Risk Segments
        self._plot_risk_segments(segment_results['risk_segments'], save_path)
        
        print(f"✅ Visualizations saved to {save_path}")
    
    def _plot_overall_summary(self, summary: Dict, save_path: str):
        """Genel özet grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Overall Customer Summary', fontsize=16, fontweight='bold')
        
        # Churn Rate
        axes[0, 0].pie([summary['overall_churn_rate'], 100 - summary['overall_churn_rate']], 
                      labels=['Churned', 'Retained'], autopct='%1.1f%%', 
                      colors=['#ff6b6b', '#4ecdc4'])
        axes[0, 0].set_title('Overall Churn Rate')
        
        # Key Metrics
        metrics = ['Total Customers', 'Churned Customers', 'Avg Monthly Charges', 'Avg Tenure (months)']
        values = [summary['total_customers'], summary['total_churned'], 
                summary['avg_monthly_charges'], summary['avg_tenure_months']]
        
        axes[0, 1].bar(metrics, values, color=['#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'])
        axes[0, 1].set_title('Key Metrics')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges Distribution
        axes[1, 0].hist([summary['avg_monthly_charges']], bins=20, color='#ff6b6b', alpha=0.7)
        axes[1, 0].set_title('Average Monthly Charges Distribution')
        axes[1, 0].set_xlabel('Monthly Charges ($)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Tenure Distribution
        axes[1, 1].hist([summary['avg_tenure_months']], bins=20, color='#4ecdc4', alpha=0.7)
        axes[1, 1].set_title('Average Tenure Distribution')
        axes[1, 1].set_xlabel('Tenure (months)')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(f"{save_path}overall_summary.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_demographic_segments(self, segments: Dict, save_path: str):
        """Demografik segment grafikleri"""
        for col, data in segments.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Demographic Segment Analysis: {col.title()}', fontsize=16, fontweight='bold')
            
            # Customer Count
            axes[0, 0].bar(data.index, data['count'], color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Segment')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[0, 1].bar(data.index, data['churn_rate'], color='#ff6b6b')
            axes[0, 1].set_title('Churn Rate by Segment')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Monthly Charges
            axes[1, 0].bar(data.index, data['avg_monthly_charges'], color='#96ceb4')
            axes[1, 0].set_title('Average Monthly Charges by Segment')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Tenure
            axes[1, 1].bar(data.index, data['avg_tenure'], color='#feca57')
            axes[1, 1].set_title('Average Tenure by Segment')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}demographic_{col}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_service_segments(self, segments: Dict, save_path: str):
        """Hizmet segment grafikleri"""
        for col, data in segments.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Service Segment Analysis: {col.title()}', fontsize=16, fontweight='bold')
            
            # Customer Count
            axes[0, 0].bar(data.index, data['count'], color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Service')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[0, 1].bar(data.index, data['churn_rate'], color='#ff6b6b')
            axes[0, 1].set_title('Churn Rate by Service')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Monthly Charges
            axes[1, 0].bar(data.index, data['avg_monthly_charges'], color='#96ceb4')
            axes[1, 0].set_title('Average Monthly Charges by Service')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Total Charges
            axes[1, 1].bar(data.index, data['avg_total_charges'], color='#feca57')
            axes[1, 1].set_title('Average Total Charges by Service')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}service_{col}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_contract_segments(self, segments: Dict, save_path: str):
        """Sözleşme segment grafikleri"""
        for col, data in segments.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Contract Segment Analysis: {col.title()}', fontsize=16, fontweight='bold')
            
            # Customer Count
            axes[0, 0].bar(data.index, data['count'], color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Contract')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[0, 1].bar(data.index, data['churn_rate'], color='#ff6b6b')
            axes[0, 1].set_title('Churn Rate by Contract')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Monthly Charges
            axes[1, 0].bar(data.index, data['avg_monthly_charges'], color='#96ceb4')
            axes[1, 0].set_title('Average Monthly Charges by Contract')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Tenure
            axes[1, 1].bar(data.index, data['avg_tenure'], color='#feca57')
            axes[1, 1].set_title('Average Tenure by Contract')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}contract_{col}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_risk_segments(self, segments: Dict, save_path: str):
        """Risk segment grafikleri"""
        for col, data in segments.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Risk Segment Analysis: {col.title()}', fontsize=16, fontweight='bold')
            
            # Customer Count
            axes[0, 0].bar(data.index, data['count'], color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Risk Level')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[0, 1].bar(data.index, data['churn_rate'], color='#ff6b6b')
            axes[0, 1].set_title('Churn Rate by Risk Level')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Monthly Charges
            axes[1, 0].bar(data.index, data['avg_monthly_charges'], color='#96ceb4')
            axes[1, 0].set_title('Average Monthly Charges by Risk Level')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Total Charges
            axes[1, 1].bar(data.index, data['avg_total_charges'], color='#feca57')
            axes[1, 1].set_title('Average Total Charges by Risk Level')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}risk_{col}.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_report(self, segment_results: Dict, save_path: str = "analytics/reports/"):
        """
        Segment analizi raporu oluştur

            segment_results: Segment analizi sonuçları
            save_path: Raporun kaydedileceği yol
        """
        print("📝 Generating segment analysis report...")
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        report_content = self._create_report_content(segment_results)
        
        # Save report
        with open(f"{save_path}segment_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Report saved to {save_path}segment_analysis_report.md")
    
    def _create_report_content(self, segment_results: Dict) -> str:
        """Rapor içeriği oluştur"""
        summary = segment_results['overall_summary']
        
        report = f"""
# Customer Segment Analysis Report

## Executive Summary

- **Total Customers**: {summary['total_customers']:,}
- **Churned Customers**: {summary['total_churned']:,}
- **Overall Churn Rate**: {summary['overall_churn_rate']}%
- **Average Monthly Charges**: ${summary['avg_monthly_charges']:,.2f}
- **Average Total Charges**: ${summary['avg_total_charges']:,.2f}
- **Average Tenure**: {summary['avg_tenure_months']:.1f} months

## Key Findings

### 1. Demographics Analysis
"""
        
        # Add demographic findings
        for col, data in segment_results['demographic_segments'].items():
            report += f"\n#### {col.title()}\n"
            report += f"| Segment | Count | Churn Rate | Avg Monthly Charges | Avg Tenure |\n"
            report += f"|---------|-------|------------|---------------------|------------|\n"
            
            for idx, row in data.iterrows():
                report += f"| {idx} | {row['count']:,} | {row['churn_rate']:.1f}% | ${row['avg_monthly_charges']:,.2f} | {row['avg_tenure']:.1f} months |\n"
        
        report += "\n### 2. Service Analysis\n"
        
        # Add service findings
        for col, data in segment_results['service_segments'].items():
            report += f"\n#### {col.title()}\n"
            report += f"| Service | Count | Churn Rate | Avg Monthly Charges | Avg Total Charges |\n"
            report += f"|---------|-------|------------|---------------------|-------------------|\n"
            
            for idx, row in data.iterrows():
                report += f"| {idx} | {row['count']:,} | {row['churn_rate']:.1f}% | ${row['avg_monthly_charges']:,.2f} | ${row['avg_total_charges']:,.2f} |\n"
        
        report += "\n### 3. Contract Analysis\n"
        
        # Add contract findings
        for col, data in segment_results['contract_segments'].items():
            report += f"\n#### {col.title()}\n"
            report += f"| Contract | Count | Churn Rate | Avg Monthly Charges | Avg Tenure |\n"
            report += f"|----------|-------|------------|---------------------|------------|\n"
            
            for idx, row in data.iterrows():
                report += f"| {idx} | {row['count']:,} | {row['churn_rate']:.1f}% | ${row['avg_monthly_charges']:,.2f} | {row['avg_tenure']:.1f} months |\n"
        
        report += "\n### 4. Risk Analysis\n"
        
        # Add risk findings
        for col, data in segment_results['risk_segments'].items():
            report += f"\n#### {col.title()}\n"
            report += f"| Risk Level | Count | Churn Rate | Avg Monthly Charges | Avg Total Charges |\n"
            report += f"|------------|-------|------------|---------------------|-------------------|\n"
            
            for idx, row in data.iterrows():
                report += f"| {idx} | {row['count']:,} | {row['churn_rate']:.1f}% | ${row['avg_monthly_charges']:,.2f} | ${row['avg_total_charges']:,.2f} |\n"
        
        report += """
## Recommendations

1. **High-Risk Segments**: Focus retention efforts on segments with churn rates above 30%
2. **Revenue Optimization**: Identify segments with high monthly charges but low churn
3. **Service Improvement**: Analyze service combinations that lead to higher churn
4. **Contract Strategy**: Review contract terms for segments with high churn rates

## Next Steps

1. Conduct deeper analysis on high-churn segments
2. Develop targeted retention strategies
3. Implement predictive models for churn prevention
4. Monitor segment performance over time
"""
        
        return report
