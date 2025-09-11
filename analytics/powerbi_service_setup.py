#!/usr/bin/env python3
"""
PowerBI Service Setup Script
===========================
Bu script, PowerBI Service (web) için optimize edilmiş veri setleri oluşturur.
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

class PowerBIServiceSetup:
    def __init__(self):
        """PowerBI Service setup sınıfı"""
        self.db_config = self._get_db_config()
        self.engine = self._create_engine()
        self.export_dir = "powerbi_service_exports"
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
            print(f"📁 PowerBI Service export dizini oluşturuldu: {self.export_dir}")
    
    def create_customer_overview_dataset(self):
        """Müşteri genel bakış veri seti oluştur"""
        print("📊 Customer Overview Dataset oluşturuluyor...")
        
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
        
        # PowerBI Service için optimize et
        df['churn_status_label'] = df['churn_status'].map({True: 'Churned', False: 'Active'})
        df['senior_citizen_label'] = df['senior_citizen'].map({True: 'Senior', False: 'Non-Senior'})
        df['partner_label'] = df['partner'].map({True: 'Has Partner', False: 'Single'})
        df['dependents_label'] = df['dependents'].map({True: 'Has Dependents', False: 'No Dependents'})
        df['phone_service_label'] = df['phone_service'].map({True: 'Yes', False: 'No'})
        df['paperless_billing_label'] = df['paperless_billing'].map({True: 'Yes', False: 'No'})
        
        # Tenure grupları oluştur
        df['tenure_group'] = pd.cut(df['tenure_months'], 
                                   bins=[0, 12, 24, 36, 60, 100], 
                                   labels=['0-12', '13-24', '25-36', '37-60', '60+'])
        
        # Monthly charges grupları oluştur
        df['monthly_charge_group'] = pd.cut(df['monthly_charges'], 
                                          bins=[0, 30, 60, 90, 120, 200], 
                                          labels=['0-30', '31-60', '61-90', '91-120', '120+'])
        
        # Total charges grupları oluştur
        df['total_charge_group'] = pd.cut(df['total_charges'], 
                                        bins=[0, 1000, 2000, 3000, 5000, 10000], 
                                        labels=['0-1K', '1K-2K', '2K-3K', '3K-5K', '5K+'])
        
        # Risk grupları oluştur
        df['risk_group'] = pd.cut(df['risk_score'], 
                                bins=[0, 0.3, 0.6, 0.8, 1.0], 
                                labels=['Low', 'Medium', 'High', 'Very High'])
        
        # CLTV grupları oluştur
        df['cltv_group'] = pd.cut(df['cltv_score'], 
                                bins=[0, 2000, 4000, 6000, 8000, 15000], 
                                labels=['0-2K', '2K-4K', '4K-6K', '6K-8K', '8K+'])
        
        # PowerBI Service için tarih formatları
        df['churn_date'] = pd.to_datetime(df['churn_date'])
        df['year'] = df['churn_date'].dt.year
        df['month'] = df['churn_date'].dt.month
        df['quarter'] = df['churn_date'].dt.quarter
        df['month_name'] = df['churn_date'].dt.month_name()
        
        # Export et
        file_path = os.path.join(self.export_dir, 'customer_overview_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Customer Overview Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_churn_analysis_dataset(self):
        """Churn analiz veri seti oluştur"""
        print("📊 Churn Analysis Dataset oluşturuluyor...")
        
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
        
        # PowerBI Service için ek hesaplamalar
        df['active_customers'] = df['total_customers'] - df['churned_customers']
        df['churn_percentage'] = df['churn_rate']
        df['retention_rate'] = 100 - df['churn_rate']
        
        # Export et
        file_path = os.path.join(self.export_dir, 'churn_analysis_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Churn Analysis Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_cltv_analysis_dataset(self):
        """CLTV analiz veri seti oluştur"""
        print("📊 CLTV Analysis Dataset oluşturuluyor...")
        
        query = """
        SELECT 
            segment_name,
            contract_type,
            payment_method,
            internet_service,
            COUNT(*) as customer_count,
            ROUND(AVG(cltv_score)::numeric, 2) as avg_cltv,
            ROUND(AVG(monthly_charges)::numeric, 2) as avg_monthly_charges,
            ROUND(AVG(total_charges)::numeric, 2) as avg_total_charges,
            ROUND(AVG(tenure_months)::numeric, 1) as avg_tenure,
            SUM(CASE WHEN churn_status = true THEN 1 ELSE 0 END) as churned_count,
            ROUND(AVG(CASE WHEN churn_status = true THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate
        FROM customer_complete_view
        GROUP BY segment_name, contract_type, payment_method, internet_service
        ORDER BY avg_cltv DESC;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # PowerBI Service için ek hesaplamalar
        df['total_cltv_value'] = df['customer_count'] * df['avg_cltv']
        df['cltv_percentage'] = (df['avg_cltv'] / df['avg_cltv'].sum()) * 100
        df['retention_rate'] = 100 - df['churn_rate']
        
        # Export et
        file_path = os.path.join(self.export_dir, 'cltv_analysis_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ CLTV Analysis Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_segment_performance_dataset(self):
        """Segment performans veri seti oluştur"""
        print("📊 Segment Performance Dataset oluşturuluyor...")
        
        query = """
        SELECT 
            segment_name,
            COUNT(*) as customer_count,
            ROUND(AVG(cltv_score)::numeric, 2) as avg_cltv,
            ROUND(AVG(monthly_charges)::numeric, 2) as avg_monthly_charges,
            ROUND(AVG(total_charges)::numeric, 2) as avg_total_charges,
            ROUND(AVG(tenure_months)::numeric, 1) as avg_tenure,
            SUM(CASE WHEN churn_status = true THEN 1 ELSE 0 END) as churned_count,
            ROUND(AVG(CASE WHEN churn_status = true THEN 1.0 ELSE 0.0 END) * 100, 2) as churn_rate,
            ROUND(AVG(risk_score)::numeric, 2) as avg_risk_score
        FROM customer_complete_view
        GROUP BY segment_name
        ORDER BY avg_cltv DESC;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # PowerBI Service için ek hesaplamalar
        df['customer_percentage'] = (df['customer_count'] / df['customer_count'].sum()) * 100
        df['total_cltv_value'] = df['customer_count'] * df['avg_cltv']
        df['cltv_percentage'] = (df['avg_cltv'] / df['avg_cltv'].sum()) * 100
        df['retention_rate'] = 100 - df['churn_rate']
        df['segment_rank'] = df['avg_cltv'].rank(ascending=False)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'segment_performance_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Segment Performance Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_ml_predictions_dataset(self):
        """ML tahmin veri seti oluştur"""
        print("📊 ML Predictions Dataset oluşturuluyor...")
        
        query = """
        SELECT 
            customer_id,
            segment_name,
            churn_status,
            "RandomForest_prediction" as rf_prediction,
            "RandomForest_probability" as rf_probability,
            "XGBoost_prediction" as xgb_prediction,
            "XGBoost_probability" as xgb_probability,
            "best_prediction" as best_prediction,
            "best_probability" as best_probability
        FROM ml_predictions
        WHERE "RandomForest_prediction" IS NOT NULL OR "XGBoost_prediction" IS NOT NULL
        ORDER BY customer_id;
        """
        
        df = pd.read_sql(query, self.engine)
        
        # PowerBI Service için optimize et
        df['churn_status_label'] = df['churn_status'].map({1: 'Churned', 0: 'Active'})
        df['rf_prediction_label'] = df['rf_prediction'].map({1: 'Churned', 0: 'Active'})
        df['xgb_prediction_label'] = df['xgb_prediction'].map({1: 'Churned', 0: 'Active'})
        df['best_prediction_label'] = df['best_prediction'].map({1: 'Churned', 0: 'Active'})
        
        # Doğruluk hesaplamaları
        df['rf_correct'] = (df['churn_status'] == df['rf_prediction']).astype(int)
        df['xgb_correct'] = (df['churn_status'] == df['xgb_prediction']).astype(int)
        df['best_correct'] = (df['churn_status'] == df['best_prediction']).astype(int)
        
        # Export et
        file_path = os.path.join(self.export_dir, 'ml_predictions_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ ML Predictions Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_time_series_dataset(self):
        """Zaman serisi veri seti oluştur"""
        print("📊 Time Series Dataset oluşturuluyor...")
        
        # Simulated time series data for trends
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')
        
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
        
        # PowerBI Service için ek hesaplamalar
        df['active_customers'] = df['total_customers'] - df['churned_customers']
        df['retention_rate'] = 100 - df['churn_rate']
        df['customer_growth_rate'] = (df['new_customers'] / df['total_customers']) * 100
        
        # Export et
        file_path = os.path.join(self.export_dir, 'time_series_dataset.csv')
        df.to_csv(file_path, index=False)
        print(f"✅ Time Series Dataset exported: {file_path}")
        print(f"   📈 Records: {len(df):,}")
        
        return df
    
    def create_powerbi_service_guide(self):
        """PowerBI Service setup rehberi oluştur"""
        guide = """
# PowerBI Service Setup Rehberi
==============================

## 🚀 PowerBI Service Kurulumu

### 1. Hesap Oluştur
1. **PowerBI Service**'e git: https://app.powerbi.com/
2. **Microsoft hesabınla giriş yap**
3. **"Create" > "Report"** seç

### 2. Veri Kaynağı Ekle
1. **"Get Data"** butonuna tıkla
2. **"Files" > "Upload"** seç
3. **CSV dosyalarını yükle**
4. **"Create"** seç

### 3. Dashboard Oluştur
1. **"Add a Chart"** seç
2. **Grafik türünü seç** (Bar, Pie, Line, etc.)
3. **Veri kaynağını seç**
4. **Boyutları ve metrikleri ayarla**

## 📊 Dashboard Tasarım Önerileri

### 1. Genel Müşteri Dağılımı
- **Pie Chart**: churn_status_label
- **Bar Chart**: gender, senior_citizen_label
- **Stacked Bar**: internet_service, contract_type
- **Donut Chart**: payment_method

### 2. Churn Trendleri
- **Line Chart**: churn_rate trend
- **Bar Chart**: segment churn comparison
- **Scatter Plot**: tenure_months vs churn_status
- **Area Chart**: monthly_charges vs churn_status

### 3. CLTV Analizi
- **Histogram**: cltv_score distribution
- **Bar Chart**: segment_name vs avg_cltv
- **Scatter Plot**: cltv_score vs churn_status
- **Box Plot**: contract_type vs cltv_score

### 4. Segment Performans
- **Treemap**: segment_name vs customer_count
- **Bar Chart**: segment_name vs avg_cltv
- **Table**: segment summary
- **Gauge**: segment performance

## 🎨 Tasarım Önerileri

### Renk Paleti:
- **Primary**: #1f77b4 (Mavi)
- **Secondary**: #ff7f0e (Turuncu)
- **Success**: #2ca02c (Yeşil)
- **Warning**: #d62728 (Kırmızı)
- **Info**: #9467bd (Mor)

### Layout:
- **Header**: Dashboard başlığı
- **Main Area**: Ana grafikler
- **Sidebar**: Filtreler
- **Footer**: Son güncelleme tarihi

## 🚀 Yayınlama
1. **"Share"** butonuna tıkla
2. **"Publish to web"** seç
3. **Embed kodları al**
4. **README.md'ye ekle**

## 🔧 Troubleshooting

### Veri Yükleme Sorunları:
- CSV dosya boyutunu kontrol et
- Veri tiplerini kontrol et
- Eksik değerleri kontrol et

### Görselleştirme Sorunları:
- Veri tiplerini kontrol et
- Eksik değerleri kontrol et
- Filtreleri kontrol et

## 📞 Destek
- **PowerBI Service**: https://app.powerbi.com/
- **PowerBI Help**: https://docs.microsoft.com/en-us/power-bi/
- **PowerBI Community**: https://community.powerbi.com/
        """
        
        file_path = os.path.join(self.export_dir, 'powerbi_service_setup_guide.md')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        print(f"✅ PowerBI Service setup guide created: {file_path}")
    
    def run_setup(self):
        """Setup işlemlerini çalıştır"""
        print("🚀 PowerBI Service Setup başlatılıyor...")
        print("=" * 50)
        
        try:
            # Ana veri setlerini export et
            self.create_customer_overview_dataset()
            self.create_churn_analysis_dataset()
            self.create_cltv_analysis_dataset()
            self.create_segment_performance_dataset()
            self.create_ml_predictions_dataset()
            self.create_time_series_dataset()
            
            # Setup rehberi oluştur
            self.create_powerbi_service_guide()
            
            print("=" * 50)
            print("✅ PowerBI Service setup tamamlandı!")
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
            print(f"❌ Setup işlemi başarısız: {e}")
            raise

def main():
    """Ana fonksiyon"""
    print("🎯 PowerBI Service Setup Tool")
    print("=" * 50)
    
    try:
        setup = PowerBIServiceSetup()
        setup.run_setup()
        
        print("\n🎉 PowerBI Service için veri hazırlığı tamamlandı!")
        print("📊 Şimdi PowerBI Service'e giriş yapabilir ve dashboard oluşturabilirsin!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
