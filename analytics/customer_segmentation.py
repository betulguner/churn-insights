"""
AI-Driven Customer Insights Platform - Customer Segmentation
KMeans clustering ile müşteri segmentasyonu modülü
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

class CustomerSegmenter:
    def __init__(self, db_config=None):
        load_dotenv()
        if db_config is None:
            self.db_config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5433)),
                'database': os.getenv('POSTGRES_DB', 'churn_analysis'),
                'user': os.getenv('POSTGRES_USER', 'churn_user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'churn_password')
            }
        else:
            self.db_config = db_config
        self.engine = self._create_db_engine()
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.kmeans_model = None
        self.optimal_k = None
        
        # Model sonuçları için klasörler oluştur
        os.makedirs('analytics/models', exist_ok=True)
        os.makedirs('analytics/plots', exist_ok=True)

    def _create_db_engine(self):
        conn_str = (
            f"postgresql+psycopg2://{self.db_config['user']}:"
            f"{self.db_config['password']}@{self.db_config['host']}:"
            f"{self.db_config['port']}/{self.db_config['database']}"
        )
        return create_engine(conn_str)

    def load_data(self, query: str) -> pd.DataFrame:
        """Veritabanından veri yükle"""
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
            print(f"✅ Data loaded: {len(df)} records")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return pd.DataFrame()

    def prepare_segmentation_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Segmentasyon için özellikleri hazırla"""
        print("🔧 Segmentation features hazırlanıyor...")
        
        # Boolean kolonları sayısal değerlere çevir
        boolean_cols = ['senior_citizen', 'partner', 'dependents', 'phone_service', 'paperless_billing', 'churn_status']
        for col in boolean_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # String kolonları sayısal değerlere çevir (Yes/No -> 1/0)
        string_cols = ['multiple_lines', 'online_security', 'online_backup', 'device_protection', 
                      'tech_support', 'streaming_tv', 'streaming_movies']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].map({'Yes': 1, 'No': 0, 'No internet service': 0})
        
        # Internet service kolonunu özel olarak işle
        if 'internet_service' in df.columns:
            df['internet_service'] = df['internet_service'].map({'DSL': 1, 'Fiber optic': 2, 'No': 0})
        
        # 1. Demografik özellikler
        df['age_group'] = pd.cut(df['senior_citizen'], 
                                bins=[-1, 0, 1], 
                                labels=['Young', 'Senior'])
        
        # 2. Hizmet özellikleri
        service_cols = ['phone_service', 'multiple_lines', 'internet_service', 
                       'online_security', 'online_backup', 'device_protection',
                       'tech_support', 'streaming_tv', 'streaming_movies']
        df['total_services'] = df[service_cols].sum(axis=1)
        
        # 3. Finansal özellikler
        df['revenue_per_month'] = df['total_charges'] / df['tenure_months'].replace(0, 1)
        df['charge_ratio'] = df['monthly_charges'] / df['total_charges'].replace(0, 1)
        
        # 4. Sözleşme özellikleri
        df['contract_months'] = df['contract_type'].map({
            'Month-to-month': 1,
            'One year': 12,
            'Two year': 24
        })
        
        # 5. Risk özellikleri
        df['risk_level'] = pd.cut(df['risk_score'], 
                                 bins=[0, 20, 40, 60, 80, 100], 
                                 labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        
        # 6. Müşteri değeri
        df['customer_value'] = df['total_charges'] * df['tenure_months'] / 12
        
        print("✅ Segmentation features hazırlandı")
        return df

    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Kategorik özellikleri encode et"""
        print("🔤 Categorical features encode ediliyor...")
        
        categorical_cols = ['gender', 'partner', 'dependents', 'phone_service',
                           'multiple_lines', 'internet_service', 'online_security',
                           'online_backup', 'device_protection', 'tech_support',
                           'streaming_tv', 'streaming_movies', 'contract_type',
                           'payment_method', 'age_group', 'risk_level']
        
        df_encoded = df.copy()
        
        for col in categorical_cols:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
        
        print("✅ Categorical features encode edildi")
        return df_encoded

    def find_optimal_k(self, X: np.ndarray, max_k: int = 10) -> int:
        """Optimal cluster sayısını bul"""
        print("🔍 Optimal cluster sayısı bulunuyor...")
        
        # Elbow method ve silhouette score
        inertias = []
        silhouette_scores = []
        calinski_scores = []
        k_range = range(2, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, kmeans.labels_))
            calinski_scores.append(calinski_harabasz_score(X, kmeans.labels_))
        
        # En iyi k'yı seç (silhouette score'a göre)
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        # Görselleştirme
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Elbow method
        axes[0].plot(k_range, inertias, 'bo-')
        axes[0].set_xlabel('Number of Clusters (k)')
        axes[0].set_ylabel('Inertia')
        axes[0].set_title('Elbow Method')
        axes[0].grid(True)
        
        # Silhouette score
        axes[1].plot(k_range, silhouette_scores, 'ro-')
        axes[1].set_xlabel('Number of Clusters (k)')
        axes[1].set_ylabel('Silhouette Score')
        axes[1].set_title('Silhouette Score')
        axes[1].grid(True)
        
        # Calinski-Harabasz score
        axes[2].plot(k_range, calinski_scores, 'go-')
        axes[2].set_xlabel('Number of Clusters (k)')
        axes[2].set_ylabel('Calinski-Harabasz Score')
        axes[2].set_title('Calinski-Harabasz Score')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.savefig('analytics/plots/optimal_k_analysis.png')
        plt.close()
        
        print(f"✅ Optimal k: {optimal_k}")
        print(f"Silhouette Score: {silhouette_scores[optimal_k-2]:.3f}")
        print(f"Calinski-Harabasz Score: {calinski_scores[optimal_k-2]:.3f}")
        
        return optimal_k

    def perform_clustering(self, X: np.ndarray, k: int = None) -> np.ndarray:
        """KMeans clustering yap"""
        print("🎯 KMeans clustering başlıyor...")
        
        if k is None:
            k = self.find_optimal_k(X)
        
        self.optimal_k = k
        
        # KMeans modeli
        self.kmeans_model = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = self.kmeans_model.fit_predict(X)
        
        # Cluster merkezlerini analiz et
        cluster_centers = self.kmeans_model.cluster_centers_
        
        print(f"✅ Clustering tamamlandı: {k} clusters")
        print(f"Silhouette Score: {silhouette_score(X, cluster_labels):.3f}")
        print(f"Calinski-Harabasz Score: {calinski_harabasz_score(X, cluster_labels):.3f}")
        
        return cluster_labels

    def analyze_clusters(self, df: pd.DataFrame, cluster_labels: np.ndarray) -> pd.DataFrame:
        """Cluster analizi yap"""
        print("📊 Cluster analizi başlıyor...")
        
        # Cluster etiketlerini ekle
        df['cluster'] = cluster_labels
        
        # Cluster özelliklerini analiz et
        cluster_analysis = df.groupby('cluster').agg({
            'customer_id': 'count',
            'churn_status': 'mean',
            'monthly_charges': 'mean',
            'total_charges': 'mean',
            'tenure_months': 'mean',
            'risk_score': 'mean',
            'total_services': 'mean',
            'revenue_per_month': 'mean',
            'customer_value': 'mean'
        }).round(2)
        
        # Cluster isimlerini belirle
        cluster_names = self._assign_cluster_names(cluster_analysis)
        df['cluster_name'] = df['cluster'].map(cluster_names)
        
        print("✅ Cluster analizi tamamlandı")
        return df

    def _assign_cluster_names(self, cluster_analysis: pd.DataFrame) -> dict:
        """Cluster'lara isim ver"""
        cluster_names = {}
        
        for cluster_id in cluster_analysis.index:
            churn_rate = cluster_analysis.loc[cluster_id, 'churn_status']
            monthly_charges = cluster_analysis.loc[cluster_id, 'monthly_charges']
            tenure = cluster_analysis.loc[cluster_id, 'tenure_months']
            total_services = cluster_analysis.loc[cluster_id, 'total_services']
            
            # Cluster karakteristiklerine göre isim ver
            if churn_rate > 0.4:
                if monthly_charges > 80:
                    cluster_names[cluster_id] = 'High Risk Premium'
                else:
                    cluster_names[cluster_id] = 'High Risk Standard'
            elif churn_rate < 0.2:
                if monthly_charges > 80:
                    cluster_names[cluster_id] = 'Low Risk Premium'
                else:
                    cluster_names[cluster_id] = 'Low Risk Standard'
            else:
                if tenure > 30:
                    cluster_names[cluster_id] = 'Mature Moderate'
                else:
                    cluster_names[cluster_id] = 'Young Moderate'
        
        return cluster_names

    def visualize_clusters(self, df: pd.DataFrame):
        """Cluster görselleştirmeleri oluştur"""
        print("📊 Cluster görselleştirmeleri oluşturuluyor...")
        
        # 1. Cluster dağılımı
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Cluster count
        plt.subplot(2, 2, 1)
        cluster_counts = df['cluster_name'].value_counts()
        plt.pie(cluster_counts.values, labels=cluster_counts.index, autopct='%1.1f%%')
        plt.title('Cluster Distribution')
        
        # Subplot 2: Churn rate by cluster
        plt.subplot(2, 2, 2)
        churn_by_cluster = df.groupby('cluster_name')['churn_status'].mean().sort_values(ascending=False)
        plt.bar(range(len(churn_by_cluster)), churn_by_cluster.values)
        plt.xticks(range(len(churn_by_cluster)), churn_by_cluster.index, rotation=45)
        plt.title('Churn Rate by Cluster')
        plt.ylabel('Churn Rate')
        
        # Subplot 3: Monthly charges by cluster
        plt.subplot(2, 2, 3)
        charges_by_cluster = df.groupby('cluster_name')['monthly_charges'].mean().sort_values(ascending=False)
        plt.bar(range(len(charges_by_cluster)), charges_by_cluster.values)
        plt.xticks(range(len(charges_by_cluster)), charges_by_cluster.index, rotation=45)
        plt.title('Average Monthly Charges by Cluster')
        plt.ylabel('Monthly Charges ($)')
        
        # Subplot 4: Tenure by cluster
        plt.subplot(2, 2, 4)
        tenure_by_cluster = df.groupby('cluster_name')['tenure_months'].mean().sort_values(ascending=False)
        plt.bar(range(len(tenure_by_cluster)), tenure_by_cluster.values)
        plt.xticks(range(len(tenure_by_cluster)), tenure_by_cluster.index, rotation=45)
        plt.title('Average Tenure by Cluster')
        plt.ylabel('Tenure (months)')
        
        plt.tight_layout()
        plt.savefig('analytics/plots/cluster_analysis.png')
        plt.close()
        
        # 2. Scatter plot: Monthly charges vs Tenure
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(df['monthly_charges'], df['tenure_months'], 
                            c=df['cluster'], cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Cluster')
        plt.xlabel('Monthly Charges ($)')
        plt.ylabel('Tenure (months)')
        plt.title('Customer Clusters: Monthly Charges vs Tenure')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('analytics/plots/cluster_scatter.png')
        plt.close()
        
        print("✅ Cluster görselleştirmeleri oluşturuldu")

    def save_segmentation_results(self, df: pd.DataFrame):
        """Segmentasyon sonuçlarını kaydet"""
        print("💾 Segmentation sonuçları kaydediliyor...")
        
        try:
            # Customer segments tablosunu güncelle
            update_query = """
            UPDATE customer_segments 
            SET 
                cluster_id = cs.cluster,
                cluster_name = cs.cluster_name,
                updated_at = CURRENT_TIMESTAMP
            FROM (
                SELECT customer_id, cluster, cluster_name 
                FROM ml_predictions 
                WHERE cluster IS NOT NULL
            ) cs
            WHERE customer_segments.customer_id = cs.customer_id
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(update_query))
                conn.commit()
            
            print("✅ Customer segments tablosu güncellendi")
            
        except Exception as e:
            print(f"❌ Error saving segmentation results: {e}")

    def run_customer_segmentation(self):
        """Customer segmentation pipeline'ını çalıştır"""
        print("🚀 Customer Segmentation Pipeline başlıyor...")
        print("=" * 60)
        
        # Veri yükle
        query = "SELECT * FROM customer_complete_view"
        df = self.load_data(query)
        
        if df.empty:
            print("❌ No data to analyze")
            return {}
        
        # Özellikleri hazırla
        df_processed = self.prepare_segmentation_features(df)
        df_encoded = self.encode_categorical_features(df_processed)
        
        # Segmentasyon için özellikleri seç
        feature_cols = ['monthly_charges', 'total_charges', 'tenure_months', 
                       'risk_score', 'total_services', 'revenue_per_month',
                       'charge_ratio', 'contract_months', 'customer_value']
        
        X = df_encoded[feature_cols].values
        
        # Özellikleri normalize et
        X_scaled = self.scaler.fit_transform(X)
        
        # Clustering yap
        cluster_labels = self.perform_clustering(X_scaled)
        
        # Cluster analizi
        df_with_clusters = self.analyze_clusters(df_processed, cluster_labels)
        
        # Görselleştirmeler
        self.visualize_clusters(df_with_clusters)
        
        # Sonuçları kaydet
        self.save_segmentation_results(df_with_clusters)
        
        # Modeli kaydet
        joblib.dump(self.kmeans_model, 'analytics/models/kmeans_model.pkl')
        joblib.dump(self.scaler, 'analytics/models/segmentation_scaler.pkl')
        joblib.dump(self.label_encoders, 'analytics/models/segmentation_encoders.pkl')
        
        print("\n✅ Customer Segmentation Pipeline tamamlandı!")
        print("=" * 60)
        
        return {
            'model': self.kmeans_model,
            'clusters': df_with_clusters,
            'optimal_k': self.optimal_k
        }

def main():
    print("🚀 Starting Customer Segmentation Analysis...")
    print("=" * 60)
    
    segmenter = CustomerSegmenter()
    print("✅ Database connection established")
    
    print("\n🎯 Running Customer Segmentation...")
    results = segmenter.run_customer_segmentation()
    
    print("\n✅ Customer Segmentation Analysis Completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
