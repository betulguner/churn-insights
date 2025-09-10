"""
AI-Driven Customer Insights Platform - Churn Prediction
Makine öğrenmesi ile churn tahmini modülü
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

class ChurnPredictor:
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
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
        
        # Model sonuçları için klasörler oluştur
        os.makedirs('analytics/models', exist_ok=True)
        os.makedirs('analytics/predictions', exist_ok=True)
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

    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Yeni özellikler oluştur"""
        print("🔧 Feature Engineering başlıyor...")
        
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
        
        # 1. Tenure Groups (Müşteri yaş grupları)
        df['tenure_group'] = pd.cut(df['tenure_months'], 
                                   bins=[0, 12, 24, 36, 48, 60, df['tenure_months'].max()], 
                                   labels=['New', 'Young', 'Mature', 'Senior', 'Veteran', 'Legend'])
        
        # 2. Charge Groups (Ücret grupları)
        df['monthly_charge_group'] = pd.cut(df['monthly_charges'], 
                                           bins=[0, 50, 70, 90, 110, df['monthly_charges'].max()], 
                                           labels=['Low', 'Medium', 'High', 'Premium', 'Elite'])
        
        # 3. Total Charge Groups (Toplam ücret grupları)
        df['total_charge_group'] = pd.cut(df['total_charges'], 
                                         bins=[0, 1000, 2000, 3000, 4000, df['total_charges'].max()], 
                                         labels=['Low', 'Medium', 'High', 'Premium', 'Elite'])
        
        # 4. Service Count (Toplam hizmet sayısı)
        service_cols = ['phone_service', 'multiple_lines', 'internet_service', 'online_security',
                       'online_backup', 'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies']
        df['service_count'] = df[service_cols].sum(axis=1)
        
        # 5. Internet Service Type (Internet hizmet türü)
        df['internet_type'] = df['internet_service'].map({
            'DSL': 'Broadband',
            'Fiber optic': 'Fiber',
            'No': 'None'
        })
        
        # 6. Payment Method Group (Ödeme yöntemi grupları)
        df['payment_group'] = df['payment_method'].map({
            'Electronic check': 'Electronic',
            'Mailed check': 'Check',
            'Bank transfer (automatic)': 'Automatic',
            'Credit card (automatic)': 'Automatic'
        })
        
        # 7. Contract Length (Sözleşme uzunluğu)
        df['contract_length'] = df['contract_type'].map({
            'Month-to-month': 1,
            'One year': 12,
            'Two year': 24
        })
        
        # 8. Risk Score Groups (Risk skoru grupları)
        df['risk_group'] = pd.cut(df['risk_score'], 
                                 bins=[0, 20, 40, 60, 80, 100], 
                                 labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        
        # 9. Churn Probability (Churn olasılığı - basit hesaplama)
        df['churn_probability'] = df['churn_status'] * 0.8 + df['risk_score'] / 100 * 0.2
        
        print("✅ Feature Engineering tamamlandı")
        return df

    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Model için özellikleri hazırla"""
        print("🎯 Feature preparation başlıyor...")
        
        # Kategorik değişkenleri encode et
        categorical_cols = ['gender', 'senior_citizen', 'partner', 'dependents',
                           'phone_service', 'multiple_lines', 'internet_service',
                           'online_security', 'online_backup', 'device_protection',
                           'tech_support', 'streaming_tv', 'streaming_movies',
                           'contract_type', 'payment_method', 'tenure_group',
                           'monthly_charge_group', 'total_charge_group', 'internet_type',
                           'payment_group', 'risk_group']
        
        df_encoded = df.copy()
        
        for col in categorical_cols:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
        
        # Sayısal özellikler
        numerical_cols = ['tenure_months', 'monthly_charges', 'total_charges', 
                          'risk_score', 'service_count', 'contract_length', 'churn_probability']
        
        # Özellik matrisi oluştur
        feature_cols = categorical_cols + numerical_cols
        feature_cols = [col for col in feature_cols if col in df_encoded.columns]
        
        X = df_encoded[feature_cols]
        y = df_encoded['churn_status']
        
        print(f"✅ Features prepared: {X.shape[1]} features, {len(y)} samples")
        return X, y, feature_cols

    def train_models(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Random Forest ve XGBoost modellerini eğit"""
        print("🤖 Model training başlıyor...")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Özellikleri normalize et
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 1. Random Forest
        print("🌲 Random Forest modeli eğitiliyor...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        rf_model.fit(X_train_scaled, y_train)
        self.models['RandomForest'] = rf_model
        
        # 2. XGBoost
        print("🚀 XGBoost modeli eğitiliyor...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        xgb_model.fit(X_train_scaled, y_train)
        self.models['XGBoost'] = xgb_model
        
        # Model performanslarını değerlendir
        self.evaluate_models(X_test_scaled, y_test)
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'X_train_scaled': X_train_scaled,
            'X_test_scaled': X_test_scaled
        }

    def evaluate_models(self, X_test: np.ndarray, y_test: pd.Series):
        """Model performanslarını değerlendir"""
        print("📊 Model evaluation başlıyor...")
        
        for name, model in self.models.items():
            print(f"\n🔍 {name} Model Performance:")
            
            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            accuracy = model.score(X_test, y_test)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            print(f"Accuracy: {accuracy:.4f}")
            print(f"AUC Score: {auc_score:.4f}")
            
            # Classification Report
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred))
            
            # Feature Importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = model.feature_importances_
                print(f"\nTop 10 Features:")
                feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                print(importance_df.head(10))
            
            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'{name} - Confusion Matrix')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.tight_layout()
            plt.savefig(f'analytics/plots/{name.lower()}_confusion_matrix.png')
            plt.close()
            
            # ROC Curve
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, label=f'{name} (AUC = {auc_score:.3f})')
            plt.plot([0, 1], [0, 1], 'k--', label='Random')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title(f'{name} - ROC Curve')
            plt.legend()
            plt.tight_layout()
            plt.savefig(f'analytics/plots/{name.lower()}_roc_curve.png')
            plt.close()

    def cross_validate_models(self, X: pd.DataFrame, y: pd.Series):
        """Cross-validation ile model performansını değerlendir"""
        print("🔄 Cross-validation başlıyor...")
        
        X_scaled = self.scaler.fit_transform(X)
        
        for name, model in self.models.items():
            print(f"\n🔍 {name} Cross-Validation:")
            
            # 5-fold cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
            cv_auc_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc')
            
            print(f"Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            print(f"AUC Score: {cv_auc_scores.mean():.4f} (+/- {cv_auc_scores.std() * 2:.4f})")

    def save_models(self):
        """Modelleri kaydet"""
        print("💾 Modeller kaydediliyor...")
        
        for name, model in self.models.items():
            model_path = f'analytics/models/{name.lower()}_model.pkl'
            joblib.dump(model, model_path)
            print(f"✅ {name} modeli kaydedildi: {model_path}")
        
        # Scaler ve encoders'ı da kaydet
        joblib.dump(self.scaler, 'analytics/models/scaler.pkl')
        joblib.dump(self.label_encoders, 'analytics/models/label_encoders.pkl')
        print("✅ Scaler ve encoders kaydedildi")

    def predict_churn(self, df: pd.DataFrame) -> pd.DataFrame:
        """Yeni veriler için churn tahmini yap"""
        print("🔮 Churn prediction başlıyor...")
        
        # Feature engineering
        df_processed = self.feature_engineering(df)
        
        # Features hazırla
        X, _, feature_cols = self.prepare_features(df_processed)
        
        # Predictions
        predictions = {}
        for name, model in self.models.items():
            X_scaled = self.scaler.transform(X)
            y_pred = model.predict(X_scaled)
            y_pred_proba = model.predict_proba(X_scaled)[:, 1]
            
            predictions[f'{name}_prediction'] = y_pred
            predictions[f'{name}_probability'] = y_pred_proba
        
        # Sonuçları DataFrame'e ekle
        result_df = df_processed.copy()
        for key, values in predictions.items():
            result_df[key] = values
        
        # En iyi modeli seç (XGBoost)
        result_df['best_prediction'] = result_df['XGBoost_prediction']
        result_df['best_probability'] = result_df['XGBoost_probability']
        
        print(f"✅ Predictions completed for {len(result_df)} customers")
        return result_df

    def run_churn_prediction(self):
        """Churn prediction pipeline'ını çalıştır"""
        print("🚀 Churn Prediction Pipeline başlıyor...")
        print("=" * 60)
        
        # Veri yükle
        query = "SELECT * FROM customer_complete_view"
        df = self.load_data(query)
        
        if df.empty:
            print("❌ No data to analyze")
            return {}
        
        # Feature engineering
        df_processed = self.feature_engineering(df)
        
        # Features hazırla
        X, y, feature_cols = self.prepare_features(df_processed)
        
        # Modelleri eğit
        train_data = self.train_models(X, y)
        
        # Cross-validation
        self.cross_validate_models(X, y)
        
        # Modelleri kaydet
        self.save_models()
        
        # Tüm veri için prediction yap
        predictions_df = self.predict_churn(df)
        
        # Sonuçları veritabanına kaydet
        self.save_predictions_to_db(predictions_df)
        
        print("\n✅ Churn Prediction Pipeline tamamlandı!")
        print("=" * 60)
        
        return {
            'models': self.models,
            'feature_importance': self.feature_importance,
            'predictions': predictions_df
        }

    def save_predictions_to_db(self, predictions_df: pd.DataFrame):
        """Prediction sonuçlarını veritabanına kaydet"""
        print("💾 Predictions veritabanına kaydediliyor...")
        
        try:
            # ML predictions tablosuna kaydet
            predictions_df.to_sql('ml_predictions', self.engine, 
                                 if_exists='replace', index=False)
            print("✅ ML predictions tablosuna kaydedildi")
            
            # Customer churn tablosunu güncelle
            update_query = """
            UPDATE customer_churn 
            SET 
                churn_prediction = ml.best_prediction,
                churn_probability = ml.best_probability,
                rf_prediction = ml.RandomForest_prediction,
                rf_probability = ml.RandomForest_probability,
                xgb_prediction = ml.XGBoost_prediction,
                xgb_probability = ml.XGBoost_probability
            FROM ml_predictions ml
            WHERE customer_churn.customer_id = ml.customer_id
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(update_query))
                conn.commit()
            
            print("✅ Customer churn tablosu güncellendi")
            
        except Exception as e:
            print(f"❌ Error saving predictions: {e}")

def main():
    print("🚀 Starting Churn Prediction Analysis...")
    print("=" * 60)
    
    predictor = ChurnPredictor()
    print("✅ Database connection established")
    
    print("\n🤖 Running Churn Prediction Models...")
    results = predictor.run_churn_prediction()
    
    print("\n✅ Churn Prediction Analysis Completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
