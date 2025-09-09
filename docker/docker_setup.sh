#!/bin/bash

# AI-Driven Customer Insights Platform - Docker Setup Script
# PostgreSQL Docker container kurulumu ve yapılandırması

echo "🐳 AI-Driven Customer Insights Platform - Docker Setup"
echo "=================================================="

# Docker kurulumunu kontrol et
if ! command -v docker &> /dev/null; then
    echo "❌ Docker kurulu değil. Kurulum için:"
    echo "1. Docker Desktop'ı indirin: https://www.docker.com/products/docker-desktop"
    echo "2. Docker Desktop'ı kurun ve başlatın"
    echo "3. Bu scripti tekrar çalıştırın"
    exit 1
fi

# Docker Compose kurulumunu kontrol et
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose kurulu değil. Kurulum için:"
    echo "brew install docker-compose"
    exit 1
fi

echo "✅ Docker ve Docker Compose kurulu"

# Docker servisinin çalışıp çalışmadığını kontrol et
if ! docker info &> /dev/null; then
    echo "❌ Docker servisi çalışmıyor. Docker Desktop'ı başlatın."
    exit 1
fi

echo "✅ Docker servisi çalışıyor"

# PostgreSQL container'ını başlat
echo "🚀 PostgreSQL container'ını başlatıyor..."

# Önce mevcut container'ları durdur
docker-compose down

# Container'ları başlat
docker-compose up -d

# Container'ların başlamasını bekle
echo "⏳ Container'ların başlamasını bekliyor..."
sleep 10

# PostgreSQL'in hazır olup olmadığını kontrol et
echo "🔍 PostgreSQL bağlantısını test ediyor..."

# Health check
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U churn_user -d churn_analysis &> /dev/null; then
        echo "✅ PostgreSQL hazır!"
        break
    fi
    echo "⏳ PostgreSQL hazırlanıyor... ($i/30)"
    sleep 2
done

# Veritabanı şemasını oluştur
echo "📋 Veritabanı şemasını oluşturuyor..."
docker-compose exec -T postgres psql -U churn_user -d churn_analysis -f /docker-entrypoint-initdb.d/init.sql

# Bağlantı bilgilerini göster
echo ""
echo "🎉 Docker PostgreSQL kurulumu tamamlandı!"
echo "=================================================="
echo "📊 Bağlantı Bilgileri:"
echo "   Host: localhost"
echo "   Port: 5433"
echo "   Database: churn_analysis"
echo "   Username: churn_user"
echo "   Password: churn_password"
echo ""
echo "🔗 pgAdmin (Web UI):"
echo "   URL: http://localhost:8080"
echo "   Email: admin@churn.com"
echo "   Password: admin123"
echo ""
echo "📝 Kullanım:"
echo "   Container'ları durdur: docker-compose down"
echo "   Container'ları başlat: docker-compose up -d"
echo "   Logları görüntüle: docker-compose logs -f"
echo "   PostgreSQL'e bağlan: docker-compose exec postgres psql -U churn_user -d churn_analysis"
echo ""

# ETL pipeline'ını test et
echo "🧪 ETL Pipeline test ediliyor..."

# Python environment'ı aktifleştir
source churn_env/bin/activate

# ETL pipeline'ını çalıştır
python etl_pipeline.py

echo ""
echo "✅ Tüm kurulum tamamlandı!"
echo "🚀 Artık 2. hafta ML modellerine geçebilirsiniz!"
