# engine/scoring.py
# ============================================================
# MODULE : Moteur de scoring qualité
# SPRINT : 3
# MODULE : E6 - Calcul des indicateurs de qualité
# TÂCHES : E6-1 à E6-7
# ============================================================

import pandas as pd
import numpy as np
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from models import Referentiel
import warnings
warnings.filterwarnings('ignore')


class ScoringEngine:
    """
    Moteur de calcul des indicateurs de qualité des données.
    Calcule les 5 dimensions : Complétude, Validité, Cohérence, Unicité, Intégrité Référentielle.
    """
    
    def __init__(self, referentiel=None):
        self.referentiel = referentiel
        self.rapport = {
            "date_execution": datetime.now().isoformat(),
            "version": "2.0",
            "scores": {},
            "score_global": 0,
            "ponderation": {},
            "details": {},
            "historique": []
        }
    
    # ============================================================
    # 1. SCORE DE COMPLÉTUDE
    # ============================================================
    
    def calculer_completude(self, df, table_name, colonnes_obligatoires=None):
        """
        Calcule le score de complétude (taux de valeurs non nulles)
        """
        print(f"\n📊 Calcul du score de COMPLÉTUDE pour {table_name}...")
        
        if colonnes_obligatoires is None:
            colonnes_obligatoires = df.columns.tolist()
        
        details = {}
        for col in colonnes_obligatoires:
            if col in df.columns:
                nb_total = len(df)
                nb_non_null = df[col].notna().sum()
                taux = (nb_non_null / nb_total * 100) if nb_total > 0 else 0
                details[col] = {
                    "nb_total": nb_total,
                    "nb_renseignes": int(nb_non_null),
                    "nb_manquants": int(nb_total - nb_non_null),
                    "taux": round(taux, 2)
                }
        
        # Score global de complétude (moyenne des taux)
        if details:
            score = np.mean([d["taux"] for d in details.values()])
        else:
            score = 0
        
        print(f"   ✅ Score de complétude : {score:.2f}%")
        
        return {
            "score": round(score, 2),
            "details": details,
            "table": table_name
        }
    
    # ============================================================
    # 2. SCORE DE VALIDITÉ
    # ============================================================
    
    def calculer_validite(self, df, table_name, contraintes=None):
        """
        Calcule le score de validité (respect des formats et contraintes)
        """
        print(f"\n📊 Calcul du score de VALIDITÉ pour {table_name}...")
        
        if contraintes is None:
            contraintes = [
                {"colonne": "EMAIL", "type": "FORMAT_EMAIL"},
                {"colonne": "PHONE", "type": "FORMAT_PHONE"},
                {"colonne": "AMOUNT", "type": "POSITIVE"}
            ]
        
        details = {}
        for contrainte in contraintes:
            col = contrainte["colonne"]
            type_contrainte = contrainte["type"]
            
            if col not in df.columns:
                continue
            
            nb_total = len(df)
            nb_valides = 0
            
            if type_contrainte == "FORMAT_EMAIL":
                nb_valides = df[col].astype(str).str.contains('@', na=False).sum()
            elif type_contrainte == "FORMAT_PHONE":
                nb_valides = df[col].astype(str).str.len().between(10, 15).sum()
            elif type_contrainte == "POSITIVE":
                nb_valides = (df[col] >= 0).sum()
            elif type_contrainte == "NOT_NULL":
                nb_valides = df[col].notna().sum()
            else:
                nb_valides = nb_total
            
            taux = (nb_valides / nb_total * 100) if nb_total > 0 else 0
            details[f"{col}_{type_contrainte}"] = {
                "colonne": col,
                "contrainte": type_contrainte,
                "nb_total": nb_total,
                "nb_valides": int(nb_valides),
                "nb_invalides": int(nb_total - nb_valides),
                "taux": round(taux, 2)
            }
        
        # Score global de validité
        if details:
            score = np.mean([d["taux"] for d in details.values()])
        else:
            score = 100  # Pas de contraintes = parfait
        
        print(f"   ✅ Score de validité : {score:.2f}%")
        
        return {
            "score": round(score, 2),
            "details": details,
            "table": table_name
        }
    
    # ============================================================
    # 3. SCORE DE COHÉRENCE
    # ============================================================
    
    def calculer_coherence(self, df, table_name, regles=None):
        """
        Calcule le score de cohérence (respect des règles métier)
        """
        print(f"\n📊 Calcul du score de COHÉRENCE pour {table_name}...")
        
        if regles is None:
            regles = [
                {"nom": "DATE_RANGE", "condition": lambda d: (d['END_DATE'].isna()) | (d['END_DATE'] >= d['START_DATE'])},
            ]
        
        details = {}
        for regle in regles:
            nom = regle["nom"]
            try:
                condition = regle["condition"](df)
                nb_total = len(df)
                nb_valides = condition.sum() if hasattr(condition, 'sum') else nb_total
                taux = (nb_valides / nb_total * 100) if nb_total > 0 else 0
                details[nom] = {
                    "nb_total": nb_total,
                    "nb_valides": int(nb_valides),
                    "nb_invalides": int(nb_total - nb_valides),
                    "taux": round(taux, 2)
                }
            except Exception as e:
                details[nom] = {"erreur": str(e), "taux": 0}
        
        if details:
            score = np.mean([d.get("taux", 0) for d in details.values()])
        else:
            score = 100
        
        print(f"   ✅ Score de cohérence : {score:.2f}%")
        
        return {
            "score": round(score, 2),
            "details": details,
            "table": table_name
        }
    
    # ============================================================
    # 4. SCORE D'UNICITÉ
    # ============================================================
    
    def calculer_unicite(self, df, table_name, cles_uniques=None):
        """
        Calcule le score d'unicité (absence de doublons)
        """
        print(f"\n📊 Calcul du score d'UNICITÉ pour {table_name}...")
        
        if cles_uniques is None:
            cles_uniques = [col for col in df.columns if 'ID' in col.upper()]
        
        details = {}
        for cle in cles_uniques:
            if cle not in df.columns:
                continue
            
            nb_total = len(df)
            nb_uniques = df[cle].nunique()
            nb_doublons = nb_total - nb_uniques
            taux = (nb_uniques / nb_total * 100) if nb_total > 0 else 0
            
            details[cle] = {
                "nb_total": nb_total,
                "nb_uniques": int(nb_uniques),
                "nb_doublons": int(nb_doublons),
                "taux": round(taux, 2)
            }
        
        if details:
            score = np.mean([d["taux"] for d in details.values()])
        else:
            score = 100
        
        print(f"   ✅ Score d'unicité : {score:.2f}%")
        
        return {
            "score": round(score, 2),
            "details": details,
            "table": table_name
        }
    
    # ============================================================
    # 5. SCORE D'INTÉGRITÉ RÉFÉRENTIELLE
    # ============================================================
    
    def calculer_integrite_referentielle(self, df, table_name, relations_fk=None):
        """
        Calcule le score d'intégrité référentielle (validité des clés étrangères)
        """
        print(f"\n📊 Calcul du score d'INTÉGRITÉ RÉFÉRENTIELLE pour {table_name}...")
        
        if relations_fk is None:
            # Par défaut, on vérifie les colonnes contenant "ID"
            relations_fk = [col for col in df.columns if 'ID' in col.upper() and col != f"{table_name}_ID"]
        
        details = {}
        for fk in relations_fk:
            if fk not in df.columns:
                continue
            
            nb_total = len(df)
            nb_non_null = df[fk].notna().sum()
            taux = (nb_non_null / nb_total * 100) if nb_total > 0 else 0
            
            details[fk] = {
                "nb_total": nb_total,
                "nb_valides": int(nb_non_null),
                "nb_invalides": int(nb_total - nb_non_null),
                "taux": round(taux, 2)
            }
        
        if details:
            score = np.mean([d["taux"] for d in details.values()])
        else:
            score = 100
        
        print(f"   ✅ Score d'intégrité référentielle : {score:.2f}%")
        
        return {
            "score": round(score, 2),
            "details": details,
            "table": table_name
        }
    
    # ============================================================
    # 6. SCORE GLOBAL PONDÉRÉ
    # ============================================================
    
    def calculer_score_global(self, scores_par_dimension, ponderation=None):
        """
        Calcule le score global pondéré
        """
        print(f"\n📊 Calcul du SCORE GLOBAL pondéré...")
        
        if ponderation is None:
            ponderation = {
                "COMPLETUDE": 20,
                "VALIDITE": 20,
                "COHERENCE": 20,
                "UNICITE": 20,
                "INTEGRITE_REFERENTIELLE": 20
            }
        
        score_global = 0
        total_poids = sum(ponderation.values())
        
        details = {}
        for dimension, poids in ponderation.items():
            if dimension in scores_par_dimension:
                score_dim = scores_par_dimension[dimension]
                contribution = (score_dim * poids) / total_poids
                score_global += contribution
                details[dimension] = {
                    "score": score_dim,
                    "poids": poids,
                    "contribution": round(contribution, 2)
                }
        
        print(f"   ✅ Score global : {score_global:.2f}%")
        
        return {
            "score": round(score_global, 2),
            "details": details,
            "ponderation": ponderation
        }
    
    # ============================================================
    # 7. CALCUL COMPLET
    # ============================================================
    
    def calculer_tous_les_scores(self, df, table_name, 
                                  colonnes_obligatoires=None,
                                  contraintes=None,
                                  regles=None,
                                  cles_uniques=None,
                                  relations_fk=None,
                                  ponderation=None):
        """
        Calcule tous les scores de qualité pour une table
        """
        print("=" * 60)
        print(f"🎯 CALCUL DES SCORES DE QUALITÉ : {table_name}")
        print("=" * 60)
        
        resultats = {
            "table": table_name,
            "nb_lignes": len(df),
            "completude": self.calculer_completude(df, table_name, colonnes_obligatoires),
            "validite": self.calculer_validite(df, table_name, contraintes),
            "coherence": self.calculer_coherence(df, table_name, regles),
            "unicite": self.calculer_unicite(df, table_name, cles_uniques),
            "integrite": self.calculer_integrite_referentielle(df, table_name, relations_fk)
        }
        
        # Score global
        scores_par_dimension = {
            "COMPLETUDE": resultats["completude"]["score"],
            "VALIDITE": resultats["validite"]["score"],
            "COHERENCE": resultats["coherence"]["score"],
            "UNICITE": resultats["unicite"]["score"],
            "INTEGRITE_REFERENTIELLE": resultats["integrite"]["score"]
        }
        
        score_global = self.calculer_score_global(scores_par_dimension, ponderation)
        resultats["score_global"] = score_global
        
        # Sauvegarder dans le rapport global
        self.rapport["scores"][table_name] = scores_par_dimension
        self.rapport["score_global"] = score_global["score"]
        self.rapport["ponderation"] = ponderation or {
            "COMPLETUDE": 20, "VALIDITE": 20, "COHERENCE": 20, 
            "UNICITE": 20, "INTEGRITE_REFERENTIELLE": 20
        }
        self.rapport["details"][table_name] = resultats
        
        return resultats
    
    # ============================================================
    # 8. VISUALISATIONS
    # ============================================================
    
    def visualiser_scores(self, fichier=None):
        """Génère 4 graphiques professionnels des scores"""
        print("\n" + "=" * 60)
        print("📊 GÉNÉRATION DES VISUALISATIONS")
        print("=" * 60)
        
        if not self.rapport["scores"]:
            print("   ⚠️ Aucun score à visualiser")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Radar chart des scores par table
        dimensions = ["COMPLETUDE", "VALIDITE", "COHERENCE", "UNICITE", "INTEGRITE_REFERENTIELLE"]
        table_names = list(self.rapport["scores"].keys())
        
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        angles += angles[:1]
        
        ax = plt.subplot(2, 2, 1, projection='polar')
        for table in table_names:
            values = [self.rapport["scores"][table].get(d, 0) for d in dimensions]
            values += values[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=table)
            ax.fill(angles, values, alpha=0.15)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_title("Scores par dimension (Radar)", fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
        
        # 2. Bar chart des scores par dimension
        if len(table_names) > 0:
            table = table_names[0]
            scores = [self.rapport["scores"][table].get(d, 0) for d in dimensions]
            
            colors = ['#2ECC71' if s >= 90 else '#F39C12' if s >= 70 else '#E63946' for s in scores]
            axes[0, 1].bar(dimensions, scores, color=colors)
            axes[0, 1].set_ylim(0, 100)
            axes[0, 1].set_ylabel('Score (%)')
            axes[0, 1].set_title(f'Scores par dimension - {table}', fontweight='bold')
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].axhline(y=90, color='green', linestyle='--', alpha=0.3, label='Excellent (90%)')
            axes[0, 1].axhline(y=70, color='orange', linestyle='--', alpha=0.3, label='Acceptable (70%)')
            axes[0, 1].legend(fontsize=8)
            axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Contribution des dimensions au score global
        score_global_details = self.rapport["details"].get(table_names[0], {}).get("score_global", {}).get("details", {})
        if score_global_details:
            dims = list(score_global_details.keys())
            contributions = [score_global_details[d]["contribution"] for d in dims]
            
            axes[1, 0].pie(contributions, labels=dims, autopct='%1.1f%%', 
                          colors=plt.cm.Set3.colors[:len(dims)], startangle=90)
            axes[1, 0].set_title('Contribution des dimensions au score global', fontweight='bold')
        
        # 4. Jauge du score global
        score_global = self.rapport["score_global"]
        ax = axes[1, 1]
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 1)
        
        couleur = '#2ECC71' if score_global >= 90 else '#F39C12' if score_global >= 70 else '#E63946'
        ax.barh([0.5], [score_global], height=0.4, color=couleur, edgecolor='black')
        ax.barh([0.5], [100], height=0.4, color='lightgray', alpha=0.3, zorder=0)
        
        ax.text(score_global / 2, 0.5, f'{score_global:.1f}%', 
                ha='center', va='center', fontsize=20, fontweight='bold', color='white')
        ax.set_yticks([])
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_title('Score Global de Qualité', fontweight='bold')
        ax.set_xlabel('Score (%)')
        
        plt.suptitle('Analyse du Scoring Qualité - MILES', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if fichier is None:
            fichier = os.path.join("..", "docs", "scoring_analysis.png")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        plt.savefig(fichier, dpi=300, bbox_inches='tight')
        print(f"   💾 Graphique sauvegardé : {fichier}")
        plt.show()
        
        return fichier
    
    # ============================================================
    # 9. RAPPORT
    # ============================================================
    
    def afficher_rapport(self):
        """Affiche le rapport complet de scoring"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE SCORING QUALITÉ")
        print("=" * 60)
        print(f"   📅 Date : {self.rapport['date_execution']}")
        print(f"   🎯 Score global : {self.rapport['score_global']:.2f}%")
        
        # Statut
        if self.rapport['score_global'] >= 90:
            print(f"      ✅ EXCELLENT - Données de très haute qualité")
        elif self.rapport['score_global'] >= 70:
            print(f"      🟡 ACCEPTABLE - Qualité correcte")
        else:
            print(f"      ❌ CRITIQUE - Qualité insuffisante")
        
        # Détail par table
        print(f"\n   📋 Scores par table :")
        for table, scores in self.rapport["scores"].items():
            print(f"\n      📊 {table} :")
            for dimension, score in scores.items():
                emoji = "✅" if score >= 90 else "🟡" if score >= 70 else "❌"
                print(f"         {emoji} {dimension} : {score:.2f}%")
    
    def exporter_rapport_json(self, fichier=None):
        """Exporte le rapport au format JSON"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "rapport_scoring.json")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        
        # Nettoyer les données pour JSON
        rapport_clean = json.loads(json.dumps(self.rapport, default=str))
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(rapport_clean, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Rapport JSON exporté : {fichier}")
        return fichier
    
    def exporter_rapport_excel(self, fichier=None):
        """Exporte le rapport au format Excel"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "rapport_scoring.xlsx")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        
        with pd.ExcelWriter(fichier, engine='openpyxl') as writer:
            # Feuille 1 : Résumé
            resume_data = [{
                "Table": table,
                "Complétude": scores.get("COMPLETUDE", 0),
                "Validité": scores.get("VALIDITE", 0),
                "Cohérence": scores.get("COHERENCE", 0),
                "Unicité": scores.get("UNICITE", 0),
                "Intégrité": scores.get("INTEGRITE_REFERENTIELLE", 0)
            } for table, scores in self.rapport["scores"].items()]
            
            if resume_data:
                pd.DataFrame(resume_data).to_excel(writer, sheet_name='Résumé', index=False)
            
            # Feuille 2 : Score global
            pd.DataFrame([{
                "Score global": self.rapport["score_global"],
                "Date": self.rapport["date_execution"]
            }]).to_excel(writer, sheet_name='Score_Global', index=False)
        
        print(f"   💾 Rapport Excel exporté : {fichier}")
        return fichier


# ============================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MOTEUR DE SCORING QUALITÉ - SPRINT 3 - E6")
    print("=" * 60)
    
    # Créer des données de test
    np.random.seed(42)
    n = 100
    
    df_contract = pd.DataFrame({
        "CONTRACT_ID": range(1, n+1),
        "REFERENCE": [f"REF{i:03d}" for i in range(1, n+1)],
        "START_DATE": pd.date_range('2024-01-01', periods=n),
        "END_DATE": pd.date_range('2025-01-01', periods=n),
        "AMOUNT": np.random.normal(20000, 5000, n).round(2),
    })
    
    # Ajouter des anomalies
    df_contract.loc[5, 'REFERENCE'] = None
    df_contract.loc[10, 'AMOUNT'] = -5000
    df_contract.loc[15, 'END_DATE'] = pd.Timestamp('2023-01-01')
    
    # Initialiser le moteur
    engine = ScoringEngine()
    
    # Calculer tous les scores
    resultats = engine.calculer_tous_les_scores(
        df_contract,
        "CONTRACT",
        colonnes_obligatoires=["CONTRACT_ID", "REFERENCE", "START_DATE", "END_DATE", "AMOUNT"],
        contraintes=[
            {"colonne": "AMOUNT", "type": "POSITIVE"},
            {"colonne": "REFERENCE", "type": "NOT_NULL"}
        ],
        regles=[
            {"nom": "DATE_RANGE", "condition": lambda d: (d['END_DATE'].isna()) | (d['END_DATE'] >= d['START_DATE'])}
        ],
        cles_uniques=["CONTRACT_ID"]
    )
    
    # Afficher le rapport
    engine.afficher_rapport()
    
    # Visualiser
    engine.visualiser_scores()
    
    # Exporter
    engine.exporter_rapport_json()
    engine.exporter_rapport_excel()
    
    print("\n" + "=" * 60)
    print("🏁 FIN - Prochaine étape : E7 - Dashboard Streamlit")
    print("=" * 60)