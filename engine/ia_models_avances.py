# engine/ia_models_avances.py
# ============================================================
# MODULE : Modèles IA Avancés (XGBoost + SHAP)
# SPRINT : 3
# MODULE : E4 - Moteur de validation IA
# ============================================================

import pandas as pd
import numpy as np
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


class XGBoostAnomalyDetector:
    """
    Détecteur d'anomalies basé sur XGBoost + SHAP
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.features = []
        self.is_fitted = False
        self.metrics = {}
        self.shap_explainer = None
    
    def fit(self, df, target_col, features=None, test_size=0.2):
        """
        Entraîne le modèle XGBoost
        
        Args:
            df: Données avec colonne cible
            target_col: Nom de la colonne cible (0 = normal, 1 = anomalie)
            features: Colonnes à utiliser
            test_size: Proportion pour le test
        """
        print("\n🧠 Entraînement XGBoost + SHAP...")
        
        if target_col not in df.columns:
            print(f"   ⚠️ Colonne cible {target_col} non trouvée")
            return
        
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != target_col]
        
        if len(features) < 1:
            print("   ⚠️ Pas assez de caractéristiques")
            return
        
        self.features = features
        
        # Préparer les données
        X = df[features].copy()
        y = df[target_col].copy()
        
        # Remplacer les valeurs manquantes
        for col in features:
            X[col] = X[col].fillna(X[col].mean())
        
        # Normaliser
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Diviser en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=self.random_state,
            stratify=y
        )
        
        # Calcul du scale_pos_weight (car souvent déséquilibré)
        n_normal = (y_train == 0).sum()
        n_anomalie = (y_train == 1).sum()
        scale_pos_weight = n_normal / n_anomalie if n_anomalie > 0 else 1
        
        # Entraîner XGBoost
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=self.random_state,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=False
        )
        
        # Évaluer
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Métriques
        self.metrics = {
            'accuracy': (y_pred == y_test).mean(),
            'precision': classification_report(y_test, y_pred, output_dict=True).get('1', {}).get('precision', 0),
            'recall': classification_report(y_test, y_pred, output_dict=True).get('1', {}).get('recall', 0),
            'f1_score': classification_report(y_test, y_pred, output_dict=True).get('1', {}).get('f1-score', 0),
            'roc_auc': roc_auc_score(y_test, y_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        # SHAP Explainer
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        self.is_fitted = True
        
        print(f"   ✅ Modèle entraîné")
        print(f"   🎯 Précision : {self.metrics['accuracy']:.2%}")
        print(f"   🎯 ROC AUC : {self.metrics['roc_auc']:.2%}")
        print(f"   📊 F1-Score (anomalies) : {self.metrics['f1_score']:.2%}")
        return self
    
    def predict(self, df):
        """Prédit les anomalies avec explications SHAP"""
        if not self.is_fitted:
            return df.assign(is_anomaly=False, probability=0)
        
        result = df.copy()
        data = result[self.features].copy()
        
        for col in self.features:
            data[col] = data[col].fillna(data[col].mean())
        
        data_scaled = self.scaler.transform(data)
        
        predictions = self.model.predict(data_scaled)
        probabilities = self.model.predict_proba(data_scaled)
        
        result['is_anomaly'] = predictions == 1
        result['probability'] = probabilities[:, 1]
        result['anomaly_score'] = -np.log(1 - probabilities[:, 1] + 1e-10)
        
        return result
    
    def explain(self, df, max_display=10):
        """
        Explique les anomalies avec SHAP
        
        Returns:
            list: Explications par ligne
        """
        if not self.is_fitted:
            return []

        data = df[self.features].copy()
        for col in self.features:
            data[col] = data[col].fillna(data[col].mean())

        data_scaled = self.scaler.transform(data)

        # Calculer les valeurs SHAP
        shap_values = self.shap_explainer.shap_values(data_scaled)

        # Expliquer chaque ligne (en utilisant enumerate pour les positions)
        explanations = []
        for pos, (idx, row) in enumerate(df.iterrows()):
            # Récupérer les features importantes
            row_shap = shap_values[pos]   # pos = 0,1,2... pas l'index original
            features_importance = list(zip(self.features, row_shap))
            features_importance.sort(key=lambda x: abs(x[1]), reverse=True)

            explanations.append({
                'row_index': idx,
                'is_anomaly': row.get('is_anomaly', False),
                'top_features': features_importance[:max_display],
                'summary': self._generer_explication(features_importance[:max_display])
            })

        return explanations
    def _generer_explication(self, top_features):
        """Génère une explication lisible"""
        parts = []
        for feature, value in top_features:
            direction = "↑" if value > 0 else "↓"
            parts.append(f"{feature} {direction} ({abs(value):.3f})")
        return " | ".join(parts)
    
    def visualiser_shap(self, df, fichier=None):
        if not self.is_fitted:
            return
        
        data = df[self.features].copy()
        for col in self.features:
            data[col] = data[col].fillna(data[col].mean())
        
        data_scaled = self.scaler.transform(data)
        shap_values = self.shap_explainer.shap_values(data_scaled)
        
        # Nouvelle API
        shap.plots.beeswarm(shap_values, feature_names=self.features, show=False, max_display=10)
        plt.title("SHAP Beeswarm - Importance des caractéristiques", fontsize=12)
        plt.tight_layout()
        
        if fichier:
            plt.savefig(fichier, dpi=150, bbox_inches='tight')
            print(f"   💾 SHAP visualisé dans : {fichier}")
        
        plt.show()
        return plt.gcf()
    
    def get_importance(self):
        """Retourne l'importance des caractéristiques"""
        if not self.is_fitted:
            return {}
        
        importance = self.model.feature_importances_
        return {feature: imp for feature, imp in zip(self.features, importance)}