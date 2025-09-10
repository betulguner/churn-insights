"""
AI-Driven Customer Insights Platform - CLTV Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.data_analyzer import DataAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class CLTVAnalyzer(DataAnalyzer):
    """CLTV analizi için özelleştirilmiş sınıf"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
    
    def analyze_cltv(self) -> Dict:
        """CLTV analizi yap"""
        print("💰 Analyzing Customer Lifetime Value...")
        
        query = "SELECT * FROM customer_complete_view"
        df = self.load_data(query)
        
        cltv_results = {
            'overall_cltv': self._calculate_overall_cltv(df),
            'segment_cltv': self._analyze_segment_cltv(df),
            'risk_cltv': self._analyze_risk_cltv(df),
            'contract_cltv': self._analyze_contract_cltv(df),
            'service_cltv': self._analyze_service_cltv(df),
            'cltv_distribution': self._analyze_cltv_distribution(df)
        }
        
        self.results['cltv_analysis'] = cltv_results
        print("✅ CLTV Analysis completed")
        return cltv_results
    
    def _calculate_overall_cltv(self, df: pd.DataFrame) -> Dict:
        """Genel CLTV hesaplaması"""
        return {
            'avg_cltv': round(df['cltv_score'].mean(), 2),
            'median_cltv': round(df['cltv_score'].median(), 2),
            'max_cltv': round(df['cltv_score'].max(), 2),
            'min_cltv': round(df['cltv_score'].min(), 2),
            'total_cltv': round(df['cltv_score'].sum(), 2)
        }
    
    def _analyze_segment_cltv(self, df: pd.DataFrame) -> Dict:
        """Segment bazlı CLTV analizi"""
        segments = ['segment_name']
        segment_analysis = {}
        
        for segment in segments:
            if segment in df.columns:
                analysis = df.groupby(segment).agg({
                    'customer_id': 'count',
                    'cltv_score': ['mean', 'median', 'sum'],
                    'churn_status': 'mean',
                    'monthly_charges': 'mean',
                    'tenure_months': 'mean'
                }).round(2)
                
                analysis.columns = ['count', 'avg_cltv', 'median_cltv', 'total_cltv', 
                                  'churn_rate', 'avg_monthly_charges', 'avg_tenure']
                analysis['churn_rate'] = analysis['churn_rate'] * 100
                
                segment_analysis[segment] = analysis.to_dict('index')
        
        return segment_analysis
    
    def _analyze_risk_cltv(self, df: pd.DataFrame) -> Dict:
        """Risk bazlı CLTV analizi"""
        df['risk_bin'] = pd.cut(df['risk_score'], 
                               bins=[0, 20, 40, 60, 80, 100], 
                               labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        
        risk_analysis = df.groupby('risk_bin').agg({
            'customer_id': 'count',
            'cltv_score': ['mean', 'median', 'sum'],
            'churn_status': 'mean',
            'monthly_charges': 'mean'
        }).round(2)
        
        risk_analysis.columns = ['count', 'avg_cltv', 'median_cltv', 'total_cltv', 
                               'churn_rate', 'avg_monthly_charges']
        risk_analysis['churn_rate'] = risk_analysis['churn_rate'] * 100
        
        return risk_analysis.to_dict('index')
    
    def _analyze_contract_cltv(self, df: pd.DataFrame) -> Dict:
        """Sözleşme bazlı CLTV analizi"""
        contract_analysis = df.groupby('contract_type').agg({
            'customer_id': 'count',
            'cltv_score': ['mean', 'median', 'sum'],
            'churn_status': 'mean',
            'monthly_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        contract_analysis.columns = ['count', 'avg_cltv', 'median_cltv', 'total_cltv', 
                                   'churn_rate', 'avg_monthly_charges', 'avg_tenure']
        contract_analysis['churn_rate'] = contract_analysis['churn_rate'] * 100
        
        return contract_analysis.to_dict('index')
    
    def _analyze_service_cltv(self, df: pd.DataFrame) -> Dict:
        """Hizmet bazlı CLTV analizi"""
        service_cols = ['internet_service', 'phone_service']
        service_analysis = {}
        
        for col in service_cols:
            if col in df.columns:
                analysis = df.groupby(col).agg({
                    'customer_id': 'count',
                    'cltv_score': ['mean', 'median', 'sum'],
                    'churn_status': 'mean',
                    'monthly_charges': 'mean'
                }).round(2)
                
                analysis.columns = ['count', 'avg_cltv', 'median_cltv', 'total_cltv', 
                                  'churn_rate', 'avg_monthly_charges']
                analysis['churn_rate'] = analysis['churn_rate'] * 100
                
                service_analysis[col] = analysis.to_dict('index')
        
        return service_analysis
    
    def _analyze_cltv_distribution(self, df: pd.DataFrame) -> Dict:
        """CLTV dağılım analizi"""
        df['cltv_bin'] = pd.cut(df['cltv_score'], 
                               bins=[0, 1000, 2000, 3000, 4000, 5000, 10000], 
                               labels=['$0-1K', '$1K-2K', '$2K-3K', '$3K-4K', '$4K-5K', '$5K+'])
        
        cltv_dist = df.groupby('cltv_bin').agg({
            'customer_id': 'count',
            'churn_status': 'mean',
            'monthly_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        cltv_dist.columns = ['count', 'churn_rate', 'avg_monthly_charges', 'avg_tenure']
        cltv_dist['churn_rate'] = cltv_dist['churn_rate'] * 100
        
        return cltv_dist.to_dict('index')
    
    def visualize_cltv_analysis(self, cltv_results: Dict, save_path: str = "analytics/plots/"):
        """CLTV analizi görselleştirmeleri"""
        print("📊 Creating CLTV visualizations...")
        os.makedirs(save_path, exist_ok=True)
        
        # Overall CLTV
        self._plot_overall_cltv(cltv_results['overall_cltv'], save_path)
        
        # Segment CLTV
        self._plot_segment_cltv(cltv_results['segment_cltv'], save_path)
        
        # Risk CLTV
        self._plot_risk_cltv(cltv_results['risk_cltv'], save_path)
        
        # Contract CLTV
        self._plot_contract_cltv(cltv_results['contract_cltv'], save_path)
        
        # CLTV Distribution
        self._plot_cltv_distribution(cltv_results['cltv_distribution'], save_path)
        
        print(f"✅ CLTV visualizations saved to {save_path}")
    
    def _plot_overall_cltv(self, overall_cltv: Dict, save_path: str):
        """Genel CLTV grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Overall CLTV Analysis', fontsize=16, fontweight='bold')
        
        # CLTV Statistics
        stats = ['Average', 'Median', 'Maximum', 'Minimum']
        values = [overall_cltv['avg_cltv'], overall_cltv['median_cltv'], 
                 overall_cltv['max_cltv'], overall_cltv['min_cltv']]
        
        axes[0, 0].bar(stats, values, color=['#45b7d1', '#96ceb4', '#feca57', '#ff6b6b'])
        axes[0, 0].set_title('CLTV Statistics')
        axes[0, 0].set_ylabel('CLTV ($)')
        
        # Total CLTV
        axes[0, 1].bar(['Total CLTV'], [overall_cltv['total_cltv']], color='#4ecdc4')
        axes[0, 1].set_title('Total CLTV')
        axes[0, 1].set_ylabel('CLTV ($)')
        
        # Summary
        axes[1, 0].text(0.1, 0.8, f"Average CLTV: ${overall_cltv['avg_cltv']:,.2f}", 
                       fontsize=12, transform=axes[1, 0].transAxes)
        axes[1, 0].text(0.1, 0.7, f"Median CLTV: ${overall_cltv['median_cltv']:,.2f}", 
                       fontsize=12, transform=axes[1, 0].transAxes)
        axes[1, 0].text(0.1, 0.6, f"Max CLTV: ${overall_cltv['max_cltv']:,.2f}", 
                       fontsize=12, transform=axes[1, 0].transAxes)
        axes[1, 0].text(0.1, 0.5, f"Min CLTV: ${overall_cltv['min_cltv']:,.2f}", 
                       fontsize=12, transform=axes[1, 0].transAxes)
        axes[1, 0].text(0.1, 0.4, f"Total CLTV: ${overall_cltv['total_cltv']:,.2f}", 
                       fontsize=12, transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('CLTV Summary')
        axes[1, 0].axis('off')
        
        # CLTV Range
        axes[1, 1].bar(['Low', 'Medium', 'High'], 
                      [overall_cltv['min_cltv'], overall_cltv['avg_cltv'], overall_cltv['max_cltv']], 
                      color=['#ff6b6b', '#feca57', '#4ecdc4'])
        axes[1, 1].set_title('CLTV Range')
        axes[1, 1].set_ylabel('CLTV ($)')
        
        plt.tight_layout()
        plt.savefig(f"{save_path}overall_cltv_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_segment_cltv(self, segment_cltv: Dict, save_path: str):
        """Segment CLTV grafiği"""
        for segment, data in segment_cltv.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'{segment.title()} CLTV Analysis', fontsize=16, fontweight='bold')
            
            segments = list(data.keys())
            counts = [data[seg]['count'] for seg in segments]
            avg_cltv = [data[seg]['avg_cltv'] for seg in segments]
            total_cltv = [data[seg]['total_cltv'] for seg in segments]
            churn_rates = [data[seg]['churn_rate'] for seg in segments]
            
            # Customer Count
            axes[0, 0].bar(segments, counts, color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Segment')
            axes[0, 0].set_ylabel('Number of Customers')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Average CLTV
            axes[0, 1].bar(segments, avg_cltv, color='#96ceb4')
            axes[0, 1].set_title('Average CLTV by Segment')
            axes[0, 1].set_ylabel('CLTV ($)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Total CLTV
            axes[1, 0].bar(segments, total_cltv, color='#feca57')
            axes[1, 0].set_title('Total CLTV by Segment')
            axes[1, 0].set_ylabel('CLTV ($)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[1, 1].bar(segments, churn_rates, color='#ff6b6b')
            axes[1, 1].set_title('Churn Rate by Segment')
            axes[1, 1].set_ylabel('Churn Rate (%)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}{segment}_cltv_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_risk_cltv(self, risk_cltv: Dict, save_path: str):
        """Risk CLTV grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Risk Level CLTV Analysis', fontsize=16, fontweight='bold')
        
        risks = list(risk_cltv.keys())
        counts = [risk_cltv[risk]['count'] for risk in risks]
        avg_cltv = [risk_cltv[risk]['avg_cltv'] for risk in risks]
        total_cltv = [risk_cltv[risk]['total_cltv'] for risk in risks]
        churn_rates = [risk_cltv[risk]['churn_rate'] for risk in risks]
        
        # Customer Count
        axes[0, 0].bar(risks, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Risk Level')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Average CLTV
        axes[0, 1].bar(risks, avg_cltv, color='#96ceb4')
        axes[0, 1].set_title('Average CLTV by Risk Level')
        axes[0, 1].set_ylabel('CLTV ($)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Total CLTV
        axes[1, 0].bar(risks, total_cltv, color='#feca57')
        axes[1, 0].set_title('Total CLTV by Risk Level')
        axes[1, 0].set_ylabel('CLTV ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[1, 1].bar(risks, churn_rates, color='#ff6b6b')
        axes[1, 1].set_title('Churn Rate by Risk Level')
        axes[1, 1].set_ylabel('Churn Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}risk_cltv_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_contract_cltv(self, contract_cltv: Dict, save_path: str):
        """Sözleşme CLTV grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Contract Type CLTV Analysis', fontsize=16, fontweight='bold')
        
        contracts = list(contract_cltv.keys())
        counts = [contract_cltv[contract]['count'] for contract in contracts]
        avg_cltv = [contract_cltv[contract]['avg_cltv'] for contract in contracts]
        total_cltv = [contract_cltv[contract]['total_cltv'] for contract in contracts]
        churn_rates = [contract_cltv[contract]['churn_rate'] for contract in contracts]
        
        # Customer Count
        axes[0, 0].bar(contracts, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Contract Type')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Average CLTV
        axes[0, 1].bar(contracts, avg_cltv, color='#96ceb4')
        axes[0, 1].set_title('Average CLTV by Contract Type')
        axes[0, 1].set_ylabel('CLTV ($)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Total CLTV
        axes[1, 0].bar(contracts, total_cltv, color='#feca57')
        axes[1, 0].set_title('Total CLTV by Contract Type')
        axes[1, 0].set_ylabel('CLTV ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[1, 1].bar(contracts, churn_rates, color='#ff6b6b')
        axes[1, 1].set_title('Churn Rate by Contract Type')
        axes[1, 1].set_ylabel('Churn Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}contract_cltv_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_cltv_distribution(self, cltv_dist: Dict, save_path: str):
        """CLTV dağılım grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('CLTV Distribution Analysis', fontsize=16, fontweight='bold')
        
        cltv_bins = list(cltv_dist.keys())
        counts = [cltv_dist[bin]['count'] for bin in cltv_bins]
        churn_rates = [cltv_dist[bin]['churn_rate'] for bin in cltv_bins]
        monthly_charges = [cltv_dist[bin]['avg_monthly_charges'] for bin in cltv_bins]
        tenure = [cltv_dist[bin]['avg_tenure'] for bin in cltv_bins]
        
        # Customer Count
        axes[0, 0].bar(cltv_bins, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by CLTV Range')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(cltv_bins, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by CLTV Range')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges
        axes[1, 0].bar(cltv_bins, monthly_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Monthly Charges by CLTV Range')
        axes[1, 0].set_ylabel('Monthly Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Tenure
        axes[1, 1].bar(cltv_bins, tenure, color='#feca57')
        axes[1, 1].set_title('Average Tenure by CLTV Range')
        axes[1, 1].set_ylabel('Tenure (months)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}cltv_distribution_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_cltv_report(self, cltv_results: Dict, save_path: str = "analytics/reports/"):
        """CLTV raporu oluştur"""
        print("📝 Generating CLTV report...")
        os.makedirs(save_path, exist_ok=True)
        
        report_content = self._create_cltv_report_content(cltv_results)
        
        with open(f"{save_path}cltv_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ CLTV report saved to {save_path}cltv_analysis_report.md")
    
    def _create_cltv_report_content(self, cltv_results: Dict) -> str:
        """CLTV raporu içeriği"""
        overall = cltv_results['overall_cltv']
        
        report = f"""
# CLTV Analysis Report

## Executive Summary

- **Average CLTV**: ${overall['avg_cltv']:,.2f}
- **Median CLTV**: ${overall['median_cltv']:,.2f}
- **Maximum CLTV**: ${overall['max_cltv']:,.2f}
- **Minimum CLTV**: ${overall['min_cltv']:,.2f}
- **Total CLTV**: ${overall['total_cltv']:,.2f}

## Key Findings

### 1. Segment Analysis
"""
        
        # Add segment findings
        for segment, data in cltv_results['segment_cltv'].items():
            report += f"\n#### {segment.title()}\n"
            for seg_name, seg_data in data.items():
                report += f"- **{seg_name}**: {seg_data['count']:,} customers, ${seg_data['avg_cltv']:,.2f} avg CLTV, {seg_data['churn_rate']:.1f}% churn rate\n"
        
        report += "\n### 2. Risk Analysis\n"
        
        # Add risk findings
        for risk, data in cltv_results['risk_cltv'].items():
            report += f"\n#### {risk}\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Average CLTV: ${data['avg_cltv']:,.2f}\n"
            report += f"- Total CLTV: ${data['total_cltv']:,.2f}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
        
        report += "\n### 3. Contract Analysis\n"
        
        # Add contract findings
        for contract, data in cltv_results['contract_cltv'].items():
            report += f"\n#### {contract}\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Average CLTV: ${data['avg_cltv']:,.2f}\n"
            report += f"- Total CLTV: ${data['total_cltv']:,.2f}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
        
        report += """
## Recommendations

1. **High CLTV Segments**: Focus retention efforts on segments with high CLTV
2. **Low CLTV Segments**: Implement strategies to increase customer value
3. **Risk Management**: Monitor high-risk customers with high CLTV
4. **Contract Strategy**: Encourage longer contracts for high CLTV customers

## Next Steps

1. Develop CLTV-based customer segmentation
2. Implement CLTV prediction models
3. Create CLTV-based retention strategies
4. Monitor CLTV trends over time
"""
        
        return report
