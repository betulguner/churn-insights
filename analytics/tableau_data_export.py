#!/usr/bin/env python3
"""
Tableau Data Export Script
==========================
Bu script, BI dashboard'ları için gerekli verileri CSV formatında export eder.
Tableau ve PowerBI için optimize edilmiş veri setleri oluşturur.
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

class TableauDataExporter:
    def __init__(self):
        """Tableau veri export sınıfı"""
        self.db_config = self._get_db_config()
        self.engine = self._create_engine()
        self.export_dir = "tableau_exports"
        self._create_export_directory()
    
    def _get_db_config(self):
        """Veritabanı konfigürasyonu"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5433'),
            'database': os.getenv('POSTGRES_DB', 'churn_analysis'),
            'user': os.getenv('POSTGRES_USER', 'churn_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'churn_password'),
        }
    
    def _create_engine(self):
        """SQLAlchemy engine oluştur"""
        connection_string = (
            f"postgresql://{self.db_config['user']}:{self.db_config['password']}"
            f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        )
        return create_engine(connection_string)
    
    def _create_export_directory(self):
        """Export dizini oluştur"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            print(f"📁 Export dizini oluşturuldu: {self.export_dir}")
    
    def export_customer_complete_view(self):
        """Müşteri tam görünümü export et"""
        print("📊 Customer Complete View export ediliyor...")
        
        query = """
        SELECT 
            customer_id,
            gender,
            senior_citizen,
            partner,
            dependents,
            phone_service,
            multiple_lines,
            internet_service,
            online_security,
            online_backup,
            device_protection,
            tech_support,
            streaming_tv,
            streaming_movies,
            contract_type,
            paperless_billing,
            payment_method,
            monthly_charges,
            total_charges,
            tenure_months,
            churn_status,
            churn_date,
            risk_score,
            segment_name,
            cltv_score
        FROM customer_complete_view
        ORDER BY customer_id;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Tableau için optimize et
        df['churn_status_label'] = df['churn_status'].map({True: 'Churned', False: 'Active'})
        df['senior_citizen_label'] = df['senior_citizen'].map({True: 'Senior', False: 'Non-Senior'})
        df['partner_label'] = df['partner'].map({True: 'Has Partner', False: 'Single'})
        df['dependents_label'] = df['dependents'].map({True: 'Has Dependents', False: 'No Dependents'})
        
        # Export et
        file_path = os.path.join(self.export_dir, 'customer_complete_data.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Customer Complete View exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def export_churn_analysis_summary(self):
        """Churn analiz özeti export et"""
        print("📊 Churn Analysis Summary export ediliyor...")
        
        query = """
        SELECT 
            contract_type,
            internet_service,
            payment_method,
            total_customers,
            churned_customers,
            churn_rate,
            avg_monthly_charges,
            avg_tenure_months
        FROM churn_analysis_view
        ORDER BY churn_rate DESC;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'churn_analysis_summary.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Churn Analysis Summary exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def export_cltv_analysis_summary(self):
        """CLTV analiz özeti export et"""
        print("📊 CLTV Analysis Summary export ediliyor...")
        
        query = """
        SELECT 
            segment_name,
            contract_type,
            payment_method,
            internet_service,
            segment_name,
            COUNT(*) as customer_count,
            ROUND(AVG(cltv_score), 2) as avg_cltv,
            ROUND(AVG(monthly_charges), 2) as avg_monthly_charges,
            ROUND(AVG(total_charges), 2) as avg_total_charges,
            ROUND(AVG(tenure_months), 1) as avg_tenure,
            SUM(CASE WHEN churn_status = true THEN 1 ELSE 0 END) as churned_count,
            ROUND(AVG(CASE WHEN churn_status = true THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate
        FROM customer_complete_view
        GROUP BY segment_name, contract_type, payment_method, internet_service
        ORDER BY avg_cltv DESC;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'cltv_analysis_summary.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ CLTV Analysis Summary exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def export_segment_analysis_summary(self):
        """Segment analiz özeti export et"""
        print("📊 Segment Analysis Summary export ediliyor...")
        
        query = """
        SELECT 
            segment_name,
            COUNT(*) as customer_count,
            ROUND(AVG(cltv_score), 2) as avg_cltv,
            ROUND(AVG(monthly_charges), 2) as avg_monthly_charges,
            ROUND(AVG(total_charges), 2) as avg_total_charges,
            ROUND(AVG(tenure_months), 1) as avg_tenure,
            SUM(CASE WHEN churn_status = true THEN 1 ELSE 0 END) as churned_count,
            ROUND(AVG(CASE WHEN churn_status = true THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate,
            ROUND(AVG(risk_score), 2) as avg_risk_score
        FROM customer_complete_view
        GROUP BY segment_name
        ORDER BY avg_cltv DESC;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'segment_analysis_summary.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Segment Analysis Summary exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def export_ml_predictions_summary(self):
        """ML tahmin özeti export et"""
        print("📊 ML Predictions Summary export ediliyor...")
        
        query = """
        SELECT 
            COUNT(*) as total_predictions,
            COUNT(CASE WHEN "RandomForest_prediction" IS NOT NULL THEN 1 END) as randomforest_predictions,
            COUNT(CASE WHEN "XGBoost_prediction" IS NOT NULL THEN 1 END) as xgboost_predictions,
            ROUND(AVG("RandomForest_probability")::numeric, 4) as avg_rf_confidence,
            ROUND(AVG("XGBoost_probability")::numeric, 4) as avg_xgb_confidence,
            ROUND(AVG("best_probability")::numeric, 4) as avg_best_confidence,
            COUNT(CASE WHEN churn_status = "RandomForest_prediction" THEN 1 END) as rf_correct,
            COUNT(CASE WHEN churn_status = "XGBoost_prediction" THEN 1 END) as xgb_correct,
            COUNT(CASE WHEN churn_status = "best_prediction" THEN 1 END) as best_correct
        FROM ml_predictions
        WHERE "RandomForest_prediction" IS NOT NULL OR "XGBoost_prediction" IS NOT NULL;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'ml_predictions_summary.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ ML Predictions Summary exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def export_time_series_data(self):
        """Zaman serisi verisi export et (simulated)"""
        print("📊 Time Series Data export ediliyor...")
        
        # Simulated time series data for trends
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
        
        time_series_data = []
        for date in dates:
            # Simulated monthly metrics
            monthly_data = {
                'month': date.strftime('%Y-%m'),
                'year': date.year,
                'month_name': date.strftime('%B'),
                'quarter': f"Q{(date.month-1)//3 + 1}",
                'total_customers': np.random.randint(7000, 7500),
                'churned_customers': np.random.randint(300, 500),
                'churn_rate': np.random.uniform(4.5, 6.5),
                'avg_cltv': np.random.uniform(3500, 4200),
                'avg_monthly_charges': np.random.uniform(65, 75),
                'new_customers': np.random.randint(200, 400)
            }
            time_series_data.append(monthly_data)
        
        df = pd.DataFrame(time_series_data)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'time_series_data.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Time Series Data exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_tableau_workbook_instructions(self):
        """Tableau workbook talimatları oluştur"""
        instructions = """
# Tableau Dashboard Talimatları
================================

## 📊 Dashboard Sayfaları

### 1. Genel Müşteri Dağılımı Dashboard
- **Veri Kaynağı**: customer_complete_data.csv
- **Grafikler**:
  - Müşteri dağılımı (Pie Chart): churn_status_label
  - Demografik dağılım (Bar Chart): gender, senior_citizen_label
  - Hizmet dağılımı (Stacked Bar): internet_service, phone_service
  - Ödeme yöntemi dağılımı (Donut Chart): payment_method
  - Sözleşme türü dağılımı (Bar Chart): contract_type

### 2. Churn Trendleri Dashboard
- **Veri Kaynağı**: churn_analysis_summary.csv, time_series_data.csv
- **Grafikler**:
  - Churn oranı trendi (Line Chart): time_series_data
  - Churn oranı by segment (Bar Chart): churn_analysis_summary
  - Risk seviyesi vs Churn (Scatter Plot): churn_analysis_summary
  - Tenure vs Churn (Area Chart): churn_analysis_summary
  - Aylık ücret vs Churn (Scatter Plot): churn_analysis_summary

### 3. CLTV Analizi Dashboard
- **Veri Kaynağı**: cltv_analysis_summary.csv
- **Grafikler**:
  - CLTV dağılımı (Histogram): avg_cltv
  - Segment CLTV karşılaştırması (Bar Chart): segment_name vs avg_cltv
  - CLTV vs Churn Rate (Scatter Plot): cltv_analysis_summary
  - Ödeme yöntemi vs CLTV (Box Plot): payment_method vs avg_cltv
  - Sözleşme türü vs CLTV (Box Plot): contract_type vs avg_cltv

### 4. Segment Performans Dashboard
- **Veri Kaynağı**: segment_analysis_summary.csv
- **Grafikler**:
  - Segment dağılımı (Treemap): segment_name vs customer_count
  - Segment CLTV karşılaştırması (Bar Chart): segment_name vs avg_cltv
  - Segment Churn Rate (Bar Chart): segment_name vs churn_rate
  - Segment Risk Score (Bar Chart): segment_name vs avg_risk_score
  - Segment Özet Tablosu (Table): Tüm metrikler

## 🎨 Dashboard Tasarım Önerileri

### Renk Paleti:
- **Primary**: #1f77b4 (Mavi)
- **Secondary**: #ff7f0e (Turuncu)
- **Success**: #2ca02c (Yeşil)
- **Warning**: #d62728 (Kırmızı)
- **Info**: #9467bd (Mor)

### Layout:
- **Header**: Dashboard başlığı ve filtreler
- **Main Area**: Ana grafikler (2x2 veya 3x2 grid)
- **Sidebar**: Filtreler ve drill-down seçenekleri
- **Footer**: Son güncelleme tarihi ve veri kaynağı

## 📈 KPI Metrikleri:
1. **Toplam Müşteri Sayısı**
2. **Genel Churn Oranı**
3. **Ortalama CLTV**
4. **Ortalama Müşteri Yaşı (Tenure)**
5. **Risk Skoru Trendi**

## 🔍 Filtreler:
- **Zaman Aralığı**: Son 12 ay
- **Segment**: Tüm segmentler
- **Churn Status**: Active/Churned
- **Contract Type**: Month-to-month/One year/Two year
- **Internet Service**: DSL/Fiber optic/No

## 📱 Responsive Tasarım:
- Desktop: 1920x1080
- Tablet: 1024x768
- Mobile: 768x1024

## 🚀 Yayınlama:
1. Tableau Public'e upload et
2. Public link oluştur
3. Embed kodları al
4. README.md'ye link ekle
        """
        
        file_path = os.path.join(self.export_dir, 'tableau_dashboard_instructions.md')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        print(f"✅ Tableau instructions created: {file_path}")
    
    def run_all_exports(self):
        """Tüm export işlemlerini çalıştır"""
        print("🚀 Tableau Data Export başlatılıyor...")
        print("=" * 50)
        
        try:
            # Ana veri setlerini export et
            self.export_customer_complete_view()
            self.export_churn_analysis_summary()
            self.export_cltv_analysis_summary()
            self.export_segment_analysis_summary()
            self.export_ml_predictions_summary()
            self.export_time_series_data()
            
            # Tableau talimatları oluştur
            self.create_tableau_workbook_instructions()
            
            print("=" * 50)
            print("✅ Tüm export işlemleri tamamlandı!")
            print(f"📁 Export dosyaları: {os.path.abspath(self.export_dir)}")
            
            # Export edilen dosyaları listele
            print("\n📋 Export edilen dosyalar:")
            for file in os.listdir(self.export_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(self.export_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({file_size:,} bytes)")
            
            print(f"\n📄 {len(os.listdir(self.export_dir))} dosya başarıyla export edildi!")
            
        except Exception as e:
            print(f"❌ Export işlemi başarısız: {e}")
            raise

def main():
    """Ana fonksiyon"""
    print("🎯 Tableau Data Export Tool")
    print("=" * 50)
    
    try:
        exporter = TableauDataExporter()
        exporter.run_all_exports()
        
        print("\n🎉 Tableau için veri hazırlığı tamamlandı!")
        print("📊 Şimdi Tableau Public'e giriş yapabilir ve dashboard'ları oluşturabilirsin!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
