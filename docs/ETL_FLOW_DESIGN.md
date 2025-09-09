# ETL Flow Design - AI-Driven Customer Insights Platform

## Overview
Bu doküman, Telco Customer Churn veri seti için tasarlanan ETL (Extract, Transform, Load) akışının detaylarını içerir.

## Veri Kaynağı Analizi

### Orijinal Veri Seti
- **Dosya**: `WA_Fn-UseC_-Telco-Customer-Churn.csv`
- **Kayıt Sayısı**: 7,043 müşteri
- **Sütun Sayısı**: 21 sütun
- **Churn Oranı**: %26.54 (1,869 müşteri)

### Veri Kalitesi
- ✅ Eksik değer yok
- ✅ Veri tipleri tutarlı
- ✅ Unique customer ID'ler mevcut

## Veri Modeli Tasarımı

### Normalizasyon Stratejisi
Orijinal flat CSV yapısını, ilişkisel veritabanı için normalize edilmiş tablolara dönüştürdük:

#### 1. customer_demographics
- **Amaç**: Müşteri demografik bilgileri
- **Anahtar**: customer_id (Primary Key)
- **Sütunlar**: gender, senior_citizen, partner, dependents

#### 2. customer_services
- **Amaç**: Müşteri hizmet abonelikleri
- **Anahtar**: customer_id (Foreign Key)
- **Sütunlar**: phone_service, internet_service, streaming_services, vb.

#### 3. customer_contracts
- **Amaç**: Sözleşme bilgileri
- **Anahtar**: customer_id (Foreign Key)
- **Sütunlar**: tenure_months, contract_type

#### 4. customer_billing
- **Amaç**: Faturalama bilgileri
- **Anahtar**: customer_id (Foreign Key)
- **Sütunlar**: monthly_charges, total_charges, payment_method

#### 5. customer_churn
- **Amaç**: Churn durumu (hedef değişken)
- **Anahtar**: customer_id (Foreign Key)
- **Sütunlar**: churn_status, churn_date

#### 6. customer_segments
- **Amaç**: ML tabanlı müşteri segmentasyonu
- **Anahtar**: customer_id (Foreign Key)
- **Sütunlar**: segment_id, segment_name, cltv_score, risk_score

## ETL Pipeline Detayları

### Extract (Çıkarma)
```python
def extract_data(csv_file_path: str) -> pd.DataFrame:
    # CSV dosyasından veri okuma
    # Veri tiplerini otomatik tespit etme
    # Temel veri kalitesi kontrolü
```

### Transform (Dönüştürme)
```python
def transform_data() -> Dict[str, pd.DataFrame]:
    # Veri temizleme ve tip dönüşümleri
    # Boolean sütunları dönüştürme
    # Eksik değerleri işleme
    # Normalizasyon (tablolara ayırma)
    # İş kurallarına göre segmentasyon
```

#### Dönüşüm Kuralları
1. **Boolean Dönüşümler**:
   - 'Yes' → True
   - 'No' → False
   - SeniorCitizen: 1 → True, 0 → False

2. **Veri Temizleme**:
   - TotalCharges: String → Numeric (eksik değerler 0 olarak)
   - Null değerler: Uygun default değerlerle doldurma

3. **Segmentasyon Kuralları**:
   - **High Value Loyal**: CLTV > 2000, Risk < 20
   - **Medium Value Stable**: CLTV > 1000, Risk < 40
   - **High Risk**: Risk > 60
   - **New Customers**: Tenure < 12 ay
   - **Standard**: Diğerleri

### Load (Yükleme)
```python
def load_data(transformed_data: Dict[str, pd.DataFrame]):
    # Foreign key constraint'lere uygun sıralama
    # Batch insert işlemleri
    # Timestamp ekleme
    # Hata yönetimi
```

#### Yükleme Sırası
1. customer_demographics (ana tablo)
2. customer_services
3. customer_contracts
4. customer_billing
5. customer_churn
6. customer_segments

### Validation (Doğrulama)
```python
def validate_data() -> Dict[str, Any]:
    # Kayıt sayısı kontrolü
    # Veri bütünlüğü kontrolü
    # İş kuralları doğrulaması
    # Churn oranı hesaplama
```

## Performans Optimizasyonları

### Veritabanı İndeksleri
- customer_demographics: gender, senior_citizen
- customer_contracts: tenure_months, contract_type
- customer_billing: monthly_charges
- customer_churn: churn_status
- customer_segments: segment_id

### View'lar
- **customer_complete_view**: Tüm müşteri bilgilerini birleştiren view
- **churn_analysis_view**: Churn analizi için özet view

## Hata Yönetimi

### Logging
- Tüm işlemler loglanır
- Hata durumları detaylı olarak kaydedilir
- Performans metrikleri takip edilir

### Exception Handling
- Database connection hataları
- Veri dönüşüm hataları
- Constraint violation hataları
- Memory overflow koruması

## Gelecek Geliştirmeler

### 2. Hafta - ML Pipeline Entegrasyonu
- Scikit-learn modelleri için veri hazırlama
- Feature engineering pipeline
- Model training ve validation

### 3. Hafta - RAG Chatbot Entegrasyonu
- BigQuery bağlantısı
- LangChain entegrasyonu
- Natural language query processing

### 4. Hafta - CI/CD Pipeline
- Docker containerization
- GitHub Actions automation
- Cloud deployment

## Teknik Detaylar

### Gereksinimler
- Python 3.8+
- PostgreSQL 15+
- Pandas, SQLAlchemy, Psycopg2

### Konfigürasyon
```python
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'churn_analysis',
    'user': 'betulguner',
    'password': ''
}
```

### Çalıştırma
```bash
# Virtual environment aktifleştirme
source churn_env/bin/activate

# ETL pipeline çalıştırma
python etl_pipeline.py
```

## Sonuçlar

### Başarı Metrikleri
- ✅ 7,043 kayıt başarıyla işlendi
- ✅ %26.54 churn oranı doğrulandı
- ✅ Tüm tablolar başarıyla oluşturuldu
- ✅ Foreign key constraint'ler korundu
- ✅ Performans indeksleri eklendi

### Veri Kalitesi
- ✅ Veri bütünlüğü sağlandı
- ✅ Normalizasyon tamamlandı
- ✅ İş kuralları uygulandı
- ✅ Segmentasyon başarılı

Bu ETL pipeline, 2. hafta ML modelleri ve 3. hafta RAG chatbot entegrasyonu için sağlam bir temel oluşturur.
