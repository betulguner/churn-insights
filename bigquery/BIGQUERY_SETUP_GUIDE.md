# Google BigQuery Kurulum Rehberi
## AI-Driven Customer Insights Platform

### 🎯 Amaç
Bu rehber, PostgreSQL veritabanındaki müşteri churn verilerini Google BigQuery'e senkronize etmek için gerekli adımları içerir.

### 📋 Ön Gereksinimler
- Google Cloud hesabı
- Google Cloud Project
- BigQuery API aktif
- Service Account ve credentials

## 🚀 Adım 1: Google Cloud Project Oluşturma

### 1.1 Google Cloud Console'a Giriş
1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin
2. Google hesabınızla giriş yapın
3. Yeni proje oluşturun veya mevcut projeyi seçin

### 1.2 Proje Oluşturma
```bash
# Proje adı önerisi
Project Name: churn-analysis-platform
Project ID: churn-analysis-platform-2025
```

## 🔧 Adım 2: BigQuery API'yi Aktifleştirme

### 2.1 API Library'den Aktifleştirme
1. Google Cloud Console'da **APIs & Services > Library** bölümüne gidin
2. "BigQuery API" arayın
3. **ENABLE** butonuna tıklayın

### 2.2 Gerekli API'ler
- BigQuery API
- BigQuery Storage API
- Cloud Storage API (opsiyonel)

## 🔐 Adım 3: Service Account Oluşturma

### 3.1 Service Account Oluşturma
1. **IAM & Admin > Service Accounts** bölümüne gidin
2. **CREATE SERVICE ACCOUNT** butonuna tıklayın
3. Detayları doldurun:
   ```
   Service account name: churn-etl-service
   Service account ID: churn-etl-service
   Description: Service account for ETL operations
   ```

### 3.2 Rolleri Atama
Service account'a şu rolleri atayın:
- **BigQuery Admin**
- **BigQuery Data Editor**
- **BigQuery Job User**

### 3.3 Credentials İndirme
1. Service account'a tıklayın
2. **KEYS** sekmesine gidin
3. **ADD KEY > Create new key** seçin
4. **JSON** formatını seçin
5. Dosyayı indirin ve güvenli bir yere kaydedin

## 📁 Adım 4: Credentials Yapılandırması

### 4.1 Environment Variable Ayarlama
```bash
# macOS/Linux
export GOOGLE_APPLICATION_CREDENTIALS="/Users/betulguner/Documents/Churn/churn-471614-a2cdb1c78845.json"

# Windows
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\credentials.json
```

### 4.2 Python'da Credentials Kullanma
```python
from google.cloud import bigquery
from google.oauth2 import service_account

# Credentials dosyası ile client oluşturma
credentials = service_account.Credentials.from_service_account_file(
    'path/to/credentials.json'
)
client = bigquery.Client(credentials=credentials, project='your-project-id')
```

## 🗄️ Adım 5: BigQuery Dataset Oluşturma

### 5.1 BigQuery Console'da Dataset Oluşturma
1. [BigQuery Console](https://console.cloud.google.com/bigquery) adresine gidin
2. Projenizi seçin
3. **CREATE DATASET** butonuna tıklayın
4. Dataset detaylarını doldurun:
   ```
   Dataset ID: churn_analysis
   Data location: US (multi-region)
   Description: Customer churn analysis dataset
   ```

### 5.2 Python ile Dataset Oluşturma
```python
from google.cloud import bigquery

client = bigquery.Client(project='your-project-id')
dataset_id = 'churn_analysis'

dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
dataset.location = "US"
dataset.description = "AI-Driven Customer Insights Platform Dataset"

dataset = client.create_dataset(dataset, exists_ok=True)
print(f"Dataset {dataset_id} created.")
```

## 📊 Adım 6: Tabloları Oluşturma

### 6.1 Schema Dosyasını Kullanma
```bash
# BigQuery schema dosyasını düzenle
# bigquery_schema.sql dosyasındaki 'your-project-id' kısmını gerçek project ID ile değiştir

# Python scripti ile tabloları oluştur
python bigquery_integration.py
```

### 6.2 Manuel Tablo Oluşturma
BigQuery Console'da SQL Editor'ü kullanarak:
```sql
-- Örnek tablo oluşturma
CREATE TABLE `your-project-id.churn_analysis.customer_demographics` (
    customer_id STRING NOT NULL,
    gender STRING NOT NULL,
    senior_citizen BOOL NOT NULL,
    partner BOOL NOT NULL,
    dependents BOOL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY customer_id, gender;
```

## 🔄 Adım 7: Veri Senkronizasyonu

### 7.1 Python Scripti ile Senkronizasyon
```python
# bigquery_integration.py dosyasını çalıştır
python bigquery_integration.py
```

### 7.2 Manuel Veri Yükleme
1. BigQuery Console'da tabloya tıklayın
2. **UPLOAD** butonuna tıklayın
3. CSV dosyasını seçin
4. Schema'yı doğrulayın
5. **CREATE TABLE** butonuna tıklayın

## 📈 Adım 8: Analiz Sorguları

### 8.1 Temel Churn Analizi
```sql
SELECT 
    contract_type,
    internet_service,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_customers,
    ROUND(COUNT(CASE WHEN churn_status = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY contract_type, internet_service
ORDER BY churn_rate DESC;
```

### 8.2 Müşteri Segmentasyonu
```sql
SELECT 
    segment_name,
    COUNT(*) as customer_count,
    AVG(cltv_score) as avg_cltv,
    AVG(risk_score) as avg_risk,
    COUNT(CASE WHEN churn_status = TRUE THEN 1 END) as churned_count
FROM `your-project-id.churn_analysis.customer_complete_view`
GROUP BY segment_name
ORDER BY avg_cltv DESC;
```

## 🔍 Adım 9: Veri Kalitesi Kontrolleri

### 9.1 Completeness Check
```sql
SELECT 
    'customer_demographics' as table_name,
    'completeness' as metric_name,
    (COUNT(*) - COUNTIF(customer_id IS NULL OR gender IS NULL)) / COUNT(*) as metric_value
FROM `your-project-id.churn_analysis.customer_demographics`;
```

### 9.2 Uniqueness Check
```sql
SELECT 
    'customer_demographics' as table_name,
    'uniqueness' as metric_name,
    COUNT(DISTINCT customer_id) / COUNT(*) as metric_value
FROM `your-project-id.churn_analysis.customer_demographics`;
```

## 💰 Adım 10: Maliyet Optimizasyonu

### 10.1 Partitioning
- Tüm tablolar `created_at` tarihine göre partition edildi
- Bu, sorgu performansını artırır ve maliyeti düşürür

### 10.2 Clustering
- Tablolar önemli sütunlara göre cluster edildi
- Bu, benzer verilerin fiziksel olarak yakın olmasını sağlar

### 10.3 Free Tier Limitleri
- **Aylık 1TB sorgu verisi** ücretsiz
- **10GB depolama** ücretsiz
- **1TB aylık aktarım** ücretsiz

## 🚨 Sorun Giderme

### Sorun 1: Authentication Hatası
```bash
# Credentials dosyasının doğru yolda olduğunu kontrol edin
echo $GOOGLE_APPLICATION_CREDENTIALS

# Credentials dosyasının geçerli olduğunu kontrol edin
gcloud auth application-default print-access-token
```

### Sorun 2: Permission Hatası
- Service account'a gerekli rolleri atadığınızdan emin olun
- BigQuery Admin rolü gerekli

### Sorun 3: Dataset Bulunamadı
- Dataset'in doğru projede oluşturulduğunu kontrol edin
- Project ID'nin doğru olduğunu kontrol edin

## 📝 Sonraki Adımlar

### 2. Hafta Hazırlığı
- BigQuery'deki veriler ML modelleri için hazır
- Scikit-learn ile churn prediction modelleri
- BigQuery ML ile doğrudan ML modelleri

### 3. Hafta Hazırlığı
- RAG chatbot için BigQuery entegrasyonu
- LangChain ile natural language query processing
- Real-time analytics dashboard

## 📞 Destek

Sorun yaşarsanız:
1. Google Cloud Console'da hata loglarını kontrol edin
2. BigQuery job history'yi inceleyin
3. Service account permissions'ları kontrol edin

---

**Not**: Bu rehber, BigQuery free tier limitleri içinde kalacak şekilde tasarlanmıştır. Production ortamında ek optimizasyonlar gerekebilir.
