
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
        