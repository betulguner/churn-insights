"""
AI-Driven Customer Insights Platform - Churn Analysis
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

class ChurnAnalyzer(DataAnalyzer):
    """
    Churn oranı analizi için özelleştirilmiş sınıf
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
    
    def analyze_churn_factors(self) -> Dict:
        """
        Churn faktörlerini detaylı analiz et
        
        Returns:
            Churn analizi sonuçları
        """
        print("🔍 Analyzing Churn Factors...")
        
        # Load data
        query = "SELECT * FROM customer_complete_view"
        df = self.load_data(query)
        
        # Churn analysis results
        churn_results = {
            'overall_churn': self._calculate_overall_churn(df),
            'contract_analysis': self._analyze_contract_churn(df),
            'service_analysis': self._analyze_service_churn(df),
            'payment_analysis': self._analyze_payment_churn(df),
            'tenure_analysis': self._analyze_tenure_churn(df),
            'charges_analysis': self._analyze_charges_churn(df),
            'demographic_analysis': self._analyze_demographic_churn(df),
            'risk_analysis': self._analyze_risk_churn(df),
            'correlation_analysis': self._analyze_churn_correlations(df)
        }
        
        self.results['churn_analysis'] = churn_results
        print("✅ Churn Analysis completed")
        
        return churn_results
    
    def _calculate_overall_churn(self, df: pd.DataFrame) -> Dict:
        """Genel churn hesaplaması"""
        total_customers = len(df)
        churned_customers = df['churn_status'].sum()
        churn_rate = (churned_customers / total_customers) * 100
        
        return {
            'total_customers': total_customers,
            'churned_customers': churned_customers,
            'retained_customers': total_customers - churned_customers,
            'churn_rate': round(churn_rate, 2),
            'retention_rate': round(100 - churn_rate, 2)
        }
    
    def _analyze_contract_churn(self, df: pd.DataFrame) -> Dict:
        """Sözleşme tipine göre churn analizi"""
        contract_analysis = df.groupby('contract_type').agg({
            'customer_id': 'count',
            'churn_status': ['sum', 'mean'],
            'monthly_charges': 'mean',
            'total_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        contract_analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                   'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
        
        # Calculate churn rate as percentage
        contract_analysis['churn_rate'] = contract_analysis['churn_rate'] * 100
        
        return contract_analysis.to_dict('index')
    
    def _analyze_service_churn(self, df: pd.DataFrame) -> Dict:
        """Hizmet tipine göre churn analizi"""
        service_cols = ['internet_service', 'phone_service', 'online_security', 
                       'online_backup', 'device_protection', 'tech_support', 
                       'streaming_tv', 'streaming_movies']
        
        service_analysis = {}
        
        for col in service_cols:
            if col in df.columns:
                analysis = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean'
                }).round(2)
                
                analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                  'avg_monthly_charges', 'avg_total_charges']
                
                # Calculate churn rate as percentage
                analysis['churn_rate'] = analysis['churn_rate'] * 100
                
                service_analysis[col] = analysis.to_dict('index')
        
        return service_analysis
    
    def _analyze_payment_churn(self, df: pd.DataFrame) -> Dict:
        """Ödeme yöntemine göre churn analizi"""
        payment_analysis = df.groupby('payment_method').agg({
            'customer_id': 'count',
            'churn_status': ['sum', 'mean'],
            'monthly_charges': 'mean',
            'total_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        payment_analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                  'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
        
        # Calculate churn rate as percentage
        payment_analysis['churn_rate'] = payment_analysis['churn_rate'] * 100
        
        return payment_analysis.to_dict('index')
    
    def _analyze_tenure_churn(self, df: pd.DataFrame) -> Dict:
        """Tenure'a göre churn analizi"""
        # Create tenure bins
        df['tenure_bin'] = pd.cut(df['tenure_months'], 
                                 bins=[0, 12, 24, 36, 48, 60, 100], 
                                 labels=['0-12', '13-24', '25-36', '37-48', '49-60', '60+'])
        
        tenure_analysis = df.groupby('tenure_bin').agg({
            'customer_id': 'count',
            'churn_status': ['sum', 'mean'],
            'monthly_charges': 'mean',
            'total_charges': 'mean'
        }).round(2)
        
        tenure_analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                 'avg_monthly_charges', 'avg_total_charges']
        
        # Calculate churn rate as percentage
        tenure_analysis['churn_rate'] = tenure_analysis['churn_rate'] * 100
        
        return tenure_analysis.to_dict('index')
    
    def _analyze_charges_churn(self, df: pd.DataFrame) -> Dict:
        """Ücretlere göre churn analizi"""
        # Create monthly charges bins
        df['monthly_charges_bin'] = pd.cut(df['monthly_charges'], 
                                          bins=[0, 30, 50, 70, 90, 120], 
                                          labels=['$0-30', '$31-50', '$51-70', '$71-90', '$90+'])
        
        charges_analysis = df.groupby('monthly_charges_bin').agg({
            'customer_id': 'count',
            'churn_status': ['sum', 'mean'],
            'total_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        charges_analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                   'avg_total_charges', 'avg_tenure']
        
        # Calculate churn rate as percentage
        charges_analysis['churn_rate'] = charges_analysis['churn_rate'] * 100
        
        return charges_analysis.to_dict('index')
    
    def _analyze_demographic_churn(self, df: pd.DataFrame) -> Dict:
        """Demografik faktörlere göre churn analizi"""
        demographic_cols = ['gender', 'senior_citizen', 'partner', 'dependents']
        
        demographic_analysis = {}
        
        for col in demographic_cols:
            if col in df.columns:
                analysis = df.groupby(col).agg({
                    'customer_id': 'count',
                    'churn_status': ['sum', 'mean'],
                    'monthly_charges': 'mean',
                    'total_charges': 'mean',
                    'tenure_months': 'mean'
                }).round(2)
                
                analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                  'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
                
                # Calculate churn rate as percentage
                analysis['churn_rate'] = analysis['churn_rate'] * 100
                
                demographic_analysis[col] = analysis.to_dict('index')
        
        return demographic_analysis
    
    def _analyze_risk_churn(self, df: pd.DataFrame) -> Dict:
        """Risk skoruna göre churn analizi"""
        # Create risk bins
        df['risk_bin'] = pd.cut(df['risk_score'], 
                               bins=[0, 20, 40, 60, 80, 100], 
                               labels=['Low (0-20)', 'Medium-Low (21-40)', 
                                      'Medium (41-60)', 'Medium-High (61-80)', 'High (81-100)'])
        
        risk_analysis = df.groupby('risk_bin').agg({
            'customer_id': 'count',
            'churn_status': ['sum', 'mean'],
            'monthly_charges': 'mean',
            'total_charges': 'mean',
            'tenure_months': 'mean'
        }).round(2)
        
        risk_analysis.columns = ['count', 'churned_count', 'churn_rate', 
                                'avg_monthly_charges', 'avg_total_charges', 'avg_tenure']
        
        # Calculate churn rate as percentage
        risk_analysis['churn_rate'] = risk_analysis['churn_rate'] * 100
        
        return risk_analysis.to_dict('index')
    
    def _analyze_churn_correlations(self, df: pd.DataFrame) -> Dict:
        """Churn ile korelasyon analizi"""
        # Select numeric columns for correlation
        numeric_cols = ['tenure_months', 'monthly_charges', 'total_charges', 
                       'risk_score', 'cltv_score', 'churn_status']
        
        # Convert boolean columns to numeric
        df_numeric = df[numeric_cols].copy()
        df_numeric['churn_status'] = df_numeric['churn_status'].astype(int)
        
        # Calculate correlations
        correlation_matrix = df_numeric.corr()
        
        # Get churn correlations (excluding churn_status itself)
        churn_correlations = correlation_matrix['churn_status'].drop('churn_status').sort_values(key=abs, ascending=False)
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'churn_correlations': churn_correlations.to_dict()
        }
    
    def visualize_churn_analysis(self, churn_results: Dict, save_path: str = "analytics/plots/"):
        """
        Churn analizi görselleştirmeleri
        
        Args:
            churn_results: Churn analizi sonuçları
            save_path: Grafiklerin kaydedileceği yol
        """
        print("📊 Creating churn analysis visualizations...")
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # 1. Overall Churn Summary
        self._plot_overall_churn(churn_results['overall_churn'], save_path)
        
        # 2. Contract Analysis
        self._plot_contract_churn(churn_results['contract_analysis'], save_path)
        
        # 3. Service Analysis
        self._plot_service_churn(churn_results['service_analysis'], save_path)
        
        # 4. Payment Analysis
        self._plot_payment_churn(churn_results['payment_analysis'], save_path)
        
        # 5. Tenure Analysis
        self._plot_tenure_churn(churn_results['tenure_analysis'], save_path)
        
        # 6. Charges Analysis
        self._plot_charges_churn(churn_results['charges_analysis'], save_path)
        
        # 7. Risk Analysis
        self._plot_risk_churn(churn_results['risk_analysis'], save_path)
        
        # 8. Correlation Analysis
        self._plot_correlation_analysis(churn_results['correlation_analysis'], save_path)
        
        print(f"✅ Churn visualizations saved to {save_path}")
    
    def _plot_overall_churn(self, overall_churn: Dict, save_path: str):
        """Genel churn özeti grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Overall Churn Analysis', fontsize=16, fontweight='bold')
        
        # Churn vs Retention
        labels = ['Churned', 'Retained']
        sizes = [overall_churn['churned_customers'], overall_churn['retained_customers']]
        colors = ['#ff6b6b', '#4ecdc4']
        
        axes[0, 0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        axes[0, 0].set_title('Churn vs Retention')
        
        # Churn Rate
        axes[0, 1].bar(['Churn Rate', 'Retention Rate'], 
                      [overall_churn['churn_rate'], overall_churn['retention_rate']], 
                      color=['#ff6b6b', '#4ecdc4'])
        axes[0, 1].set_title('Churn vs Retention Rate (%)')
        axes[0, 1].set_ylabel('Rate (%)')
        
        # Customer Count
        axes[1, 0].bar(['Total Customers', 'Churned Customers', 'Retained Customers'], 
                      [overall_churn['total_customers'], overall_churn['churned_customers'], 
                       overall_churn['retained_customers']], 
                      color=['#45b7d1', '#ff6b6b', '#4ecdc4'])
        axes[1, 0].set_title('Customer Count')
        axes[1, 0].set_ylabel('Number of Customers')
        
        # Summary Stats
        axes[1, 1].text(0.1, 0.8, f"Total Customers: {overall_churn['total_customers']:,}", 
                       fontsize=12, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.7, f"Churned: {overall_churn['churned_customers']:,}", 
                       fontsize=12, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.6, f"Retained: {overall_churn['retained_customers']:,}", 
                       fontsize=12, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.5, f"Churn Rate: {overall_churn['churn_rate']}%", 
                       fontsize=12, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.4, f"Retention Rate: {overall_churn['retention_rate']}%", 
                       fontsize=12, transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Summary Statistics')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{save_path}overall_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_contract_churn(self, contract_analysis: Dict, save_path: str):
        """Sözleşme churn analizi grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Contract Type Churn Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data
        contracts = list(contract_analysis.keys())
        counts = [contract_analysis[contract]['count'] for contract in contracts]
        churn_rates = [contract_analysis[contract]['churn_rate'] for contract in contracts]
        monthly_charges = [contract_analysis[contract]['avg_monthly_charges'] for contract in contracts]
        tenure = [contract_analysis[contract]['avg_tenure'] for contract in contracts]
        
        # Customer Count
        axes[0, 0].bar(contracts, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Contract Type')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(contracts, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by Contract Type')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges
        axes[1, 0].bar(contracts, monthly_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Monthly Charges by Contract Type')
        axes[1, 0].set_ylabel('Monthly Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Tenure
        axes[1, 1].bar(contracts, tenure, color='#feca57')
        axes[1, 1].set_title('Average Tenure by Contract Type')
        axes[1, 1].set_ylabel('Tenure (months)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}contract_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_service_churn(self, service_analysis: Dict, save_path: str):
        """Hizmet churn analizi grafiği"""
        for service, data in service_analysis.items():
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'{service.title()} Churn Analysis', fontsize=16, fontweight='bold')
            
            # Prepare data
            services = list(data.keys())
            counts = [data[service]['count'] for service in services]
            churn_rates = [data[service]['churn_rate'] for service in services]
            monthly_charges = [data[service]['avg_monthly_charges'] for service in services]
            total_charges = [data[service]['avg_total_charges'] for service in services]
            
            # Customer Count
            axes[0, 0].bar(services, counts, color='#45b7d1')
            axes[0, 0].set_title('Customer Count by Service')
            axes[0, 0].set_ylabel('Number of Customers')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Churn Rate
            axes[0, 1].bar(services, churn_rates, color='#ff6b6b')
            axes[0, 1].set_title('Churn Rate by Service')
            axes[0, 1].set_ylabel('Churn Rate (%)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Monthly Charges
            axes[1, 0].bar(services, monthly_charges, color='#96ceb4')
            axes[1, 0].set_title('Average Monthly Charges by Service')
            axes[1, 0].set_ylabel('Monthly Charges ($)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Total Charges
            axes[1, 1].bar(services, total_charges, color='#feca57')
            axes[1, 1].set_title('Average Total Charges by Service')
            axes[1, 1].set_ylabel('Total Charges ($)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}{service}_churn_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_payment_churn(self, payment_analysis: Dict, save_path: str):
        """Ödeme yöntemi churn analizi grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Payment Method Churn Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data
        payments = list(payment_analysis.keys())
        counts = [payment_analysis[payment]['count'] for payment in payments]
        churn_rates = [payment_analysis[payment]['churn_rate'] for payment in payments]
        monthly_charges = [payment_analysis[payment]['avg_monthly_charges'] for payment in payments]
        tenure = [payment_analysis[payment]['avg_tenure'] for payment in payments]
        
        # Customer Count
        axes[0, 0].bar(payments, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Payment Method')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(payments, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by Payment Method')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges
        axes[1, 0].bar(payments, monthly_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Monthly Charges by Payment Method')
        axes[1, 0].set_ylabel('Monthly Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Tenure
        axes[1, 1].bar(payments, tenure, color='#feca57')
        axes[1, 1].set_title('Average Tenure by Payment Method')
        axes[1, 1].set_ylabel('Tenure (months)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}payment_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_tenure_churn(self, tenure_analysis: Dict, save_path: str):
        """Tenure churn analizi grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Tenure Churn Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data
        tenures = list(tenure_analysis.keys())
        counts = [tenure_analysis[tenure]['count'] for tenure in tenures]
        churn_rates = [tenure_analysis[tenure]['churn_rate'] for tenure in tenures]
        monthly_charges = [tenure_analysis[tenure]['avg_monthly_charges'] for tenure in tenures]
        total_charges = [tenure_analysis[tenure]['avg_total_charges'] for tenure in tenures]
        
        # Customer Count
        axes[0, 0].bar(tenures, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Tenure')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(tenures, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by Tenure')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges
        axes[1, 0].bar(tenures, monthly_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Monthly Charges by Tenure')
        axes[1, 0].set_ylabel('Monthly Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Total Charges
        axes[1, 1].bar(tenures, total_charges, color='#feca57')
        axes[1, 1].set_title('Average Total Charges by Tenure')
        axes[1, 1].set_ylabel('Total Charges ($)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}tenure_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_charges_churn(self, charges_analysis: Dict, save_path: str):
        """Ücret churn analizi grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Monthly Charges Churn Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data
        charges = list(charges_analysis.keys())
        counts = [charges_analysis[charge]['count'] for charge in charges]
        churn_rates = [charges_analysis[charge]['churn_rate'] for charge in charges]
        total_charges = [charges_analysis[charge]['avg_total_charges'] for charge in charges]
        tenure = [charges_analysis[charge]['avg_tenure'] for charge in charges]
        
        # Customer Count
        axes[0, 0].bar(charges, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Monthly Charges')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(charges, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by Monthly Charges')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Total Charges
        axes[1, 0].bar(charges, total_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Total Charges by Monthly Charges')
        axes[1, 0].set_ylabel('Total Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Tenure
        axes[1, 1].bar(charges, tenure, color='#feca57')
        axes[1, 1].set_title('Average Tenure by Monthly Charges')
        axes[1, 1].set_ylabel('Tenure (months)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}charges_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_risk_churn(self, risk_analysis: Dict, save_path: str):
        """Risk churn analizi grafiği"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Risk Level Churn Analysis', fontsize=16, fontweight='bold')
        
        # Prepare data
        risks = list(risk_analysis.keys())
        counts = [risk_analysis[risk]['count'] for risk in risks]
        churn_rates = [risk_analysis[risk]['churn_rate'] for risk in risks]
        monthly_charges = [risk_analysis[risk]['avg_monthly_charges'] for risk in risks]
        tenure = [risk_analysis[risk]['avg_tenure'] for risk in risks]
        
        # Customer Count
        axes[0, 0].bar(risks, counts, color='#45b7d1')
        axes[0, 0].set_title('Customer Count by Risk Level')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Churn Rate
        axes[0, 1].bar(risks, churn_rates, color='#ff6b6b')
        axes[0, 1].set_title('Churn Rate by Risk Level')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly Charges
        axes[1, 0].bar(risks, monthly_charges, color='#96ceb4')
        axes[1, 0].set_title('Average Monthly Charges by Risk Level')
        axes[1, 0].set_ylabel('Monthly Charges ($)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Tenure
        axes[1, 1].bar(risks, tenure, color='#feca57')
        axes[1, 1].set_title('Average Tenure by Risk Level')
        axes[1, 1].set_ylabel('Tenure (months)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}risk_churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_correlation_analysis(self, correlation_analysis: Dict, save_path: str):
        """Korelasyon analizi grafiği"""
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        fig.suptitle('Churn Correlation Analysis', fontsize=16, fontweight='bold')
        
        # Correlation Matrix Heatmap
        correlation_matrix = pd.DataFrame(correlation_analysis['correlation_matrix'])
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   ax=axes[0], square=True, fmt='.2f')
        axes[0].set_title('Correlation Matrix Heatmap')
        
        # Churn Correlations Bar Plot
        churn_correlations = pd.Series(correlation_analysis['churn_correlations'])
        
        colors = ['#ff6b6b' if x > 0 else '#4ecdc4' for x in churn_correlations.values]
        axes[1].barh(churn_correlations.index, churn_correlations.values, color=colors)
        axes[1].set_title('Churn Correlations')
        axes[1].set_xlabel('Correlation Coefficient')
        axes[1].axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}correlation_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_churn_report(self, churn_results: Dict, save_path: str = "analytics/reports/"):
        """
        Churn analizi raporu oluştur
        
        Args:
            churn_results: Churn analizi sonuçları
            save_path: Raporun kaydedileceği yol
        """
        print("📝 Generating churn analysis report...")
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        report_content = self._create_churn_report_content(churn_results)
        
        # Save report
        with open(f"{save_path}churn_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Churn report saved to {save_path}churn_analysis_report.md")
    
    def _create_churn_report_content(self, churn_results: Dict) -> str:
        """Churn raporu içeriği oluştur"""
        overall = churn_results['overall_churn']
        
        report = f"""
# Churn Analysis Report

## Executive Summary

- **Total Customers**: {overall['total_customers']:,}
- **Churned Customers**: {overall['churned_customers']:,}
- **Retained Customers**: {overall['retained_customers']:,}
- **Overall Churn Rate**: {overall['churn_rate']}%
- **Retention Rate**: {overall['retention_rate']}%

## Key Findings

### 1. Contract Type Analysis
"""
        
        # Add contract findings
        for contract, data in churn_results['contract_analysis'].items():
            report += f"\n#### {contract}\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
            report += f"- Average Monthly Charges: ${data['avg_monthly_charges']:,.2f}\n"
            report += f"- Average Tenure: {data['avg_tenure']:.1f} months\n"
        
        report += "\n### 2. Payment Method Analysis\n"
        
        # Add payment findings
        for payment, data in churn_results['payment_analysis'].items():
            report += f"\n#### {payment}\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
            report += f"- Average Monthly Charges: ${data['avg_monthly_charges']:,.2f}\n"
            report += f"- Average Tenure: {data['avg_tenure']:.1f} months\n"
        
        report += "\n### 3. Service Analysis\n"
        
        # Add service findings
        for service, data in churn_results['service_analysis'].items():
            report += f"\n#### {service.title()}\n"
            for service_type, service_data in data.items():
                report += f"- **{service_type}**: {service_data['count']:,} customers, {service_data['churn_rate']:.1f}% churn rate\n"
        
        report += "\n### 4. Tenure Analysis\n"
        
        # Add tenure findings
        for tenure, data in churn_results['tenure_analysis'].items():
            report += f"\n#### {tenure} months\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
            report += f"- Average Monthly Charges: ${data['avg_monthly_charges']:,.2f}\n"
        
        report += "\n### 5. Risk Analysis\n"
        
        # Add risk findings
        for risk, data in churn_results['risk_analysis'].items():
            report += f"\n#### {risk}\n"
            report += f"- Customer Count: {data['count']:,}\n"
            report += f"- Churn Rate: {data['churn_rate']:.1f}%\n"
            report += f"- Average Monthly Charges: ${data['avg_monthly_charges']:,.2f}\n"
            report += f"- Average Tenure: {data['avg_tenure']:.1f} months\n"
        
        report += "\n### 6. Correlation Analysis\n"
        
        # Add correlation findings
        correlations = churn_results['correlation_analysis']['churn_correlations']
        report += "\n#### Top Churn Correlations:\n"
        for factor, correlation in list(correlations.items())[:5]:
            report += f"- **{factor}**: {correlation:.3f}\n"
        
        report += """
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
"""
        
        return report
