# Dashboard Tasarım Rehberi
==========================

## 🎨 Genel Tasarım Prensipleri

### Renk Paleti:
- **Primary**: #1f77b4 (Mavi) - Ana metrikler
- **Secondary**: #ff7f0e (Turuncu) - İkincil metrikler
- **Success**: #2ca02c (Yeşil) - Pozitif değerler
- **Warning**: #d62728 (Kırmızı) - Negatif değerler
- **Info**: #9467bd (Mor) - Bilgi metrikleri
- **Neutral**: #808080 (Gri) - Nötr değerler

### Layout:
- **Header**: Dashboard başlığı ve filtreler (80px yükseklik)
- **Main Area**: Ana grafikler (2x2 veya 3x2 grid)
- **Sidebar**: Filtreler ve drill-down seçenekleri (250px genişlik)
- **Footer**: Son güncelleme tarihi ve veri kaynağı (40px yükseklik)

## 📊 Dashboard Sayfaları

### 1. Genel Müşteri Dağılımı Dashboard

#### KPI'lar (Üst Kısım):
- **Toplam Müşteri**: 7,043
- **Churn Oranı**: 26.54%
- **Ortalama Tenure**: 32.4 ay
- **Ortalama Aylık Ücret**: $64.76

#### Grafikler:
- **Müşteri Durumu**: Pie Chart (churn_status_label)
- **Cinsiyet Dağılımı**: Donut Chart (gender)
- **Yaş Grubu**: Bar Chart (senior_citizen_label)
- **Partner Durumu**: Bar Chart (partner_label)
- **Bağımlı Durumu**: Bar Chart (dependents_label)
- **İnternet Hizmeti**: Stacked Bar Chart (internet_service)
- **Sözleşme Türü**: Bar Chart (contract_type)
- **Ödeme Yöntemi**: Pie Chart (payment_method)

#### Filtreler:
- **Churn Status**: Active/Churned
- **Gender**: Male/Female
- **Senior Citizen**: Yes/No
- **Contract Type**: Month-to-month/One year/Two year

### 2. Churn Trendleri Dashboard

#### KPI'lar (Üst Kısım):
- **Genel Churn Oranı**: 26.54%
- **En Yüksek Churn Segmenti**: [Segment Name]
- **En Düşük Churn Segmenti**: [Segment Name]
- **Ortalama Churn Oranı**: 26.54%

#### Grafikler:
- **Churn Oranı Trendi**: Line Chart (time_series_data)
- **Segment Churn Karşılaştırması**: Bar Chart (churn_analysis_dataset)
- **Sözleşme Türü vs Churn**: Stacked Bar Chart
- **Ödeme Yöntemi vs Churn**: Stacked Bar Chart
- **Tenure vs Churn**: Scatter Plot
- **Aylık Ücret vs Churn**: Scatter Plot

#### Filtreler:
- **Zaman Aralığı**: Son 12 ay
- **Segment**: Tüm segmentler
- **Contract Type**: Month-to-month/One year/Two year
- **Payment Method**: Electronic check/Mailed check/Bank transfer/Credit card

### 3. CLTV Analizi Dashboard

#### KPI'lar (Üst Kısım):
- **Ortalama CLTV**: $4,650.32
- **En Yüksek CLTV Segmenti**: [Segment Name]
- **En Düşük CLTV Segmenti**: [Segment Name]
- **CLTV Trendi**: [Time Series]

#### Grafikler:
- **CLTV Dağılımı**: Histogram (avg_cltv)
- **Segment CLTV Karşılaştırması**: Bar Chart
- **CLTV vs Churn Rate**: Scatter Plot
- **Sözleşme Türü vs CLTV**: Box Plot
- **Ödeme Yöntemi vs CLTV**: Box Plot
- **Tenure vs CLTV**: Scatter Plot

#### Filtreler:
- **Segment**: Tüm segmentler
- **Contract Type**: Month-to-month/One year/Two year
- **Payment Method**: Electronic check/Mailed check/Bank transfer/Credit card
- **CLTV Range**: 0-2K/2K-4K/4K-6K/6K-8K/8K+

### 4. Segment Performans Dashboard

#### KPI'lar (Üst Kısım):
- **Toplam Segment Sayısı**: 5
- **En Büyük Segment**: [Segment Name]
- **En Küçük Segment**: [Segment Name]
- **Segment Çeşitliliği**: [Metric]

#### Grafikler:
- **Segment Dağılımı**: Treemap (segment_name vs customer_count)
- **Segment CLTV Karşılaştırması**: Bar Chart
- **Segment Churn Rate**: Bar Chart
- **Segment Risk Score**: Bar Chart
- **Segment Özet Tablosu**: Table

#### Filtreler:
- **Segment**: Tüm segmentler
- **Customer Count Range**: 0-1000/1000-2000/2000+
- **CLTV Range**: 0-2K/2K-4K/4K-6K/6K-8K/8K+
- **Churn Rate Range**: 0-10%/10-20%/20-30%/30%+

### 5. ML Tahmin Dashboard

#### KPI'lar (Üst Kısım):
- **Random Forest Doğruluğu**: 79.2%
- **XGBoost Doğruluğu**: 80.1%
- **En İyi Model Doğruluğu**: 80.1%
- **Toplam Tahmin Sayısı**: 7,043

#### Grafikler:
- **Model Doğruluk Karşılaştırması**: Bar Chart
- **Confusion Matrix**: Heatmap
- **ROC Curve**: Line Chart
- **Tahmin Güvenilirliği**: Histogram
- **Segment Bazlı Doğruluk**: Bar Chart

#### Filtreler:
- **Model**: Random Forest/XGBoost/Best
- **Segment**: Tüm segmentler
- **Confidence Level**: 0-0.5/0.5-0.7/0.7-0.9/0.9-1.0
- **Prediction**: Churned/Active

## 📱 Responsive Tasarım

### Desktop (1920x1080):
- **Grid**: 3x2 (6 grafik)
- **KPI**: 4 adet üstte
- **Filtreler**: Sol sidebar

### Tablet (1024x768):
- **Grid**: 2x2 (4 grafik)
- **KPI**: 4 adet üstte
- **Filtreler**: Üstte horizontal

### Mobile (768x1024):
- **Grid**: 1x1 (1 grafik)
- **KPI**: 2 adet üstte
- **Filtreler**: Accordion style

## 🔍 Interaktivite

### Drill-down:
- **Segment → Customer**: Segment seçimi → Müşteri detayları
- **Time → Month**: Yıl seçimi → Ay detayları
- **Contract → Payment**: Sözleşme seçimi → Ödeme detayları

### Cross-filtering:
- **Segment seçimi**: Diğer grafiklerde filtreleme
- **Zaman seçimi**: Tüm grafiklerde filtreleme
- **Churn status**: Tüm metriklerde filtreleme

### Tooltip:
- **Hover**: Detaylı bilgi gösterimi
- **Click**: Drill-down seçenekleri
- **Double-click**: Full screen mode

## 🚀 Yayınlama

### Tableau Public:
1. Dashboard'ları Tableau Public'e upload et
2. Public link oluştur
3. Embed kodları al
4. README.md'ye link ekle

### PowerBI Service:
1. Dashboard'ları PowerBI Service'e publish et
2. Public link oluştur
3. Embed kodları al
4. README.md'ye link ekle

## 📊 Veri Kaynakları

### Tableau:
- `tableau_exports/customer_complete_data.csv`
- `tableau_exports/churn_analysis_summary.csv`
- `tableau_exports/cltv_analysis_summary.csv`
- `tableau_exports/segment_analysis_summary.csv`
- `tableau_exports/ml_predictions_summary.csv`
- `tableau_exports/time_series_data.csv`

### PowerBI:
- `powerbi_exports/customer_overview_dataset.csv`
- `powerbi_exports/churn_analysis_dataset.csv`
- `powerbi_exports/cltv_analysis_dataset.csv`
- `powerbi_exports/segment_performance_dataset.csv`
- `powerbi_exports/ml_predictions_dataset.csv`
- `powerbi_exports/time_series_dataset.csv`

## 🔧 Troubleshooting

### Veri Yükleme Sorunları:
- CSV dosya boyutlarını kontrol et
- Veri tiplerini kontrol et
- Eksik değerleri kontrol et

### Görselleştirme Sorunları:
- Veri tiplerini kontrol et
- Eksik değerleri kontrol et
- Filtreleri kontrol et

### Performans Sorunları:
- Veri boyutunu kontrol et
- Gereksiz hesaplamaları kaldır
- Cache kullan

## 📞 Destek
- **Tableau Community**: https://community.tableau.com/
- **PowerBI Community**: https://community.powerbi.com/
- **Microsoft Docs**: https://docs.microsoft.com/en-us/power-bi/
- **Tableau Docs**: https://help.tableau.com/
