
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
        