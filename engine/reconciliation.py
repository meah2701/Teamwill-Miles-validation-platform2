# engine/reconciliation.py
# ============================================================
# MODULE : Moteur de réconciliation (Version Avancée)
# SPRINT : 3
# MODULE : E5 - Module de réconciliation
# TÂCHES : E5-1 à E5-4 + Extensions
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


class ReconciliationEngine:
    """
    Moteur de réconciliation avancé.
    Compare plusieurs jeux de données (source MILES vs cible SAP).
    """
    
    def __init__(self, referentiel=None):
        self.referentiel = referentiel
        self.rapport = {
            "date_execution": datetime.now().isoformat(),
            "version": "2.0",
            "comparaisons": [],
            "total_ecarts": 0,
            "ecarts_critiques": 0,
            "ecarts_mineurs": 0,
            "manquants_source": 0,
            "manquants_cible": 0,
            "score_reconciliation": 0,
            "recommandations": []
        }
    
    # ============================================================
    # 1. COMPARAISON PRINCIPALE
    # ============================================================
    
    def comparer(self, table_name, source_data, cible_data, cle,
                 tolerances=None, colonnes_critiques=None, 
                 colonnes_a_comparer=None):
        """
        Compare les données source et cible sur une clé commune
        """
        print(f"\n{'='*60}")
        print(f"🔍 RÉCONCILIATION : {table_name}")
        print(f"{'='*60}")
        print(f"   Clé de jointure : {cle}")
        
        resultat = {
            "table": table_name,
            "cle": cle,
            "source_count": len(source_data),
            "cible_count": len(cible_data),
            "cles_communes": 0,
            "manquants_source": [],
            "manquants_cible": [],
            "ecarts": [],
            "nb_ecarts": 0,
            "nb_ecarts_critiques": 0,
            "nb_ecarts_mineurs": 0,
            "taux_correspondance": 0,
            "taux_ecart": 0,
            "statistiques_par_colonne": {}
        }
        
        # Vérification de la clé
        if cle not in source_data.columns or cle not in cible_data.columns:
            print(f"   ⚠️ Clé {cle} absente des données")
            resultat["erreur"] = f"Clé {cle} absente"
            return resultat
        
        # Copie et conversion en string
        source = source_data.copy()
        cible = cible_data.copy()
        source[cle] = source[cle].astype(str)
        cible[cle] = cible[cle].astype(str)
        
        # 1. Analyse des clés
        cles_source = set(source[cle])
        cles_cible = set(cible[cle])
        cles_communes = cles_source & cles_cible
        
        manquants_source = cles_cible - cles_source
        manquants_cible = cles_source - cles_cible
        
        resultat["cles_communes"] = len(cles_communes)
        resultat["manquants_source"] = list(manquants_source)
        resultat["manquants_cible"] = list(manquants_cible)
        
        # 2. Statistiques de correspondance
        total_cles = len(cles_source | cles_cible)
        resultat["taux_correspondance"] = (len(cles_communes) / total_cles * 100) if total_cles > 0 else 0
        
        print(f"\n   📊 Analyse des clés :")
        print(f"      - Clés communes : {len(cles_communes)}")
        print(f"      - Manquants source : {len(manquants_source)}")
        print(f"      - Manquants cible : {len(manquants_cible)}")
        print(f"      - Taux de correspondance : {resultat['taux_correspondance']:.1f}%")
        
        # 3. Comparaison des enregistrements communs
        if len(cles_communes) > 0:
            print(f"\n   🔍 Comparaison des {len(cles_communes)} enregistrements communs...")
            
            # Déterminer les colonnes à comparer
            if colonnes_a_comparer is None:
                colonnes_source = set(source.columns) - {cle}
                colonnes_cible = set(cible.columns) - {cle}
                colonnes_a_comparer = list(colonnes_source & colonnes_cible)
            
            print(f"      - Colonnes comparées : {len(colonnes_a_comparer)}")
            
            # Index pour accès rapide
            source_dict = {str(row[cle]): row.to_dict() for _, row in source.iterrows()}
            cible_dict = {str(row[cle]): row.to_dict() for _, row in cible.iterrows()}
            
            # Statistiques par colonne
            for col in colonnes_a_comparer:
                resultat["statistiques_par_colonne"][col] = {
                    "nb_ecarts": 0,
                    "critique": self._est_critique(col, colonnes_critiques)
                }
            
            # Comparer chaque enregistrement
            for cle_valeur in cles_communes:
                source_row = source_dict.get(cle_valeur, {})
                cible_row = cible_dict.get(cle_valeur, {})
                
                for col in colonnes_a_comparer:
                    val_source = source_row.get(col)
                    val_cible = cible_row.get(col)
                    
                    if self._est_ecart(val_source, val_cible, tolerances, col):
                        est_critique = self._est_critique(col, colonnes_critiques)
                        
                        ecart = {
                            "cle_valeur": cle_valeur,
                            "colonne": col,
                            "valeur_source": str(val_source),
                            "valeur_cible": str(val_cible),
                            "critique": est_critique,
                            "type_ecart": self._classifier_ecart(val_source, val_cible)
                        }
                        resultat["ecarts"].append(ecart)
                        resultat["statistiques_par_colonne"][col]["nb_ecarts"] += 1
                        
                        if est_critique:
                            resultat["nb_ecarts_critiques"] += 1
                        else:
                            resultat["nb_ecarts_mineurs"] += 1
        
        # 4. Calcul des taux
        resultat["nb_ecarts"] = len(resultat["ecarts"])
        
        if len(cles_communes) > 0:
            resultat["taux_ecart"] = (resultat["nb_ecarts"] / (len(cles_communes) * len(colonnes_a_comparer))) * 100
        else:
            resultat["taux_ecart"] = 0
        
        # 5. Recommandations automatiques
        resultat["recommandations"] = self._generer_recommandations(resultat)
        
        # 6. Affichage du résumé
        self._afficher_resume(resultat)
        
        # 7. Mise à jour du rapport global
        self.rapport["comparaisons"].append(resultat)
        self.rapport["total_ecarts"] += resultat["nb_ecarts"]
        self.rapport["ecarts_critiques"] += resultat["nb_ecarts_critiques"]
        self.rapport["ecarts_mineurs"] += resultat["nb_ecarts_mineurs"]
        self.rapport["manquants_source"] += len(manquants_source)
        self.rapport["manquants_cible"] += len(manquants_cible)
        
        return resultat
    
    # ============================================================
    # 2. MÉTHODES UTILITAIRES
    # ============================================================
    
    def _est_ecart(self, val_source, val_cible, tolerances, colonne):
        """Détermine si deux valeurs sont en écart"""
        if pd.isna(val_source) and pd.isna(val_cible):
            return False
        if pd.isna(val_source) or pd.isna(val_cible):
            return True
        
        try:
            if isinstance(val_source, (int, float, np.number)) and isinstance(val_cible, (int, float, np.number)):
                if tolerances and colonne in tolerances:
                    if abs(val_source - val_cible) <= tolerances[colonne]:
                        return False
                return float(val_source) != float(val_cible)
        except:
            pass
        
        return str(val_source).strip() != str(val_cible).strip()
    
    def _est_critique(self, colonne, colonnes_critiques=None):
        """Détermine si un écart est critique"""
        if colonnes_critiques:
            return colonne.upper() in [c.upper() for c in colonnes_critiques]
        
        colonnes_defaut = [
            "REFERENCE", "CONTRACT_ID", "CUSTOMER_ID", "FLEETVEHICLE_ID",
            "AMOUNT", "MONTANT", "VIN", "LICENSE_PLATE", "ID", "CODE"
        ]
        return colonne.upper() in [c.upper() for c in colonnes_defaut]
    
    def _classifier_ecart(self, val_source, val_cible):
        """Classifie le type d'écart"""
        if pd.isna(val_source) and not pd.isna(val_cible):
            return "manquant_source"
        if not pd.isna(val_source) and pd.isna(val_cible):
            return "manquant_cible"
        if isinstance(val_source, (int, float)) and isinstance(val_cible, (int, float)):
            return "difference_numerique"
        return "difference_texte"
    
    def _generer_recommandations(self, resultat):
        """Génère des recommandations automatiques"""
        recommandations = []
        
        if resultat["taux_correspondance"] < 90:
            recommandations.append({
                "priorite": "HAUTE",
                "categorie": "Correspondance",
                "message": f"Taux de correspondance faible ({resultat['taux_correspondance']:.1f}%). Vérifier les clés de jointure."
            })
        
        if resultat["nb_ecarts_critiques"] > 0:
            recommandations.append({
                "priorite": "HAUTE",
                "categorie": "Critique",
                "message": f"{resultat['nb_ecarts_critiques']} écarts critiques détectés. Investigation immédiate requise."
            })
        
        # Analyser les colonnes avec le plus d'écarts
        if resultat["statistiques_par_colonne"]:
            col_max = max(resultat["statistiques_par_colonne"].items(), 
                         key=lambda x: x[1]["nb_ecarts"])
            if col_max[1]["nb_ecarts"] > 0:
                recommandations.append({
                    "priorite": "MOYENNE",
                    "categorie": "Colonne",
                    "message": f"La colonne '{col_max[0]}' concentre {col_max[1]['nb_ecarts']} écarts. Vérifier la logique de transformation."
                })
        
        if len(resultat["manquants_source"]) > 0:
            recommandations.append({
                "priorite": "MOYENNE",
                "categorie": "Manquants",
                "message": f"{len(resultat['manquants_source'])} enregistrements manquants dans la source. Vérifier l'extraction."
            })
        
        return recommandations
    
    def _afficher_resume(self, resultat):
        """Affiche le résumé de la comparaison"""
        print(f"\n   📊 RÉSUMÉ :")
        print(f"      - Source : {resultat['source_count']} enregistrements")
        print(f"      - Cible : {resultat['cible_count']} enregistrements")
        print(f"      - Clés communes : {resultat['cles_communes']}")
        print(f"      - Taux de correspondance : {resultat['taux_correspondance']:.1f}%")
        print(f"      - Écarts trouvés : {resultat['nb_ecarts']}")
        print(f"        * Critiques : {resultat['nb_ecarts_critiques']} 🔴")
        print(f"        * Mineurs : {resultat['nb_ecarts_mineurs']} 🟡")
        print(f"      - Taux d'écart : {resultat['taux_ecart']:.2f}%")
        
        if resultat["recommandations"]:
            print(f"\n   💡 RECOMMANDATIONS :")
            for reco in resultat["recommandations"]:
                print(f"      [{reco['priorite']}] {reco['message']}")
    
    # ============================================================
    # 3. VISUALISATIONS
    # ============================================================
    
    def visualiser_ecarts(self, fichier=None):
        """Génère 4 graphiques professionnels des écarts"""
        print("\n" + "=" * 60)
        print("📊 GÉNÉRATION DES VISUALISATIONS")
        print("=" * 60)
        
        if not self.rapport["comparaisons"]:
            print("   ⚠️ Aucune comparaison à visualiser")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Répartition des écarts par table
        tables = [c["table"] for c in self.rapport["comparaisons"]]
        ecarts_critiques = [c["nb_ecarts_critiques"] for c in self.rapport["comparaisons"]]
        ecarts_mineurs = [c["nb_ecarts_mineurs"] for c in self.rapport["comparaisons"]]
        
        x = np.arange(len(tables))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, ecarts_critiques, width, label='Critiques', color='#E63946')
        axes[0, 0].bar(x + width/2, ecarts_mineurs, width, label='Mineurs', color='#F39C12')
        axes[0, 0].set_xlabel('Tables')
        axes[0, 0].set_ylabel('Nombre d\'écarts')
        axes[0, 0].set_title('Répartition des écarts par table', fontweight='bold')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(tables, rotation=45, ha='right')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Taux de correspondance par table
        taux = [c["taux_correspondance"] for c in self.rapport["comparaisons"]]
        couleurs = ['#2ECC71' if t >= 90 else '#F39C12' if t >= 70 else '#E63946' for t in taux]
        
        axes[0, 1].barh(tables, taux, color=couleurs)
        axes[0, 1].set_xlabel('Taux de correspondance (%)')
        axes[0, 1].set_title('Taux de correspondance par table', fontweight='bold')
        axes[0, 1].axvline(x=90, color='green', linestyle='--', alpha=0.5, label='Objectif 90%')
        axes[0, 1].legend()
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # 3. Top 10 des colonnes avec le plus d'écarts
        colonnes_ecarts = {}
        for comp in self.rapport["comparaisons"]:
            for col, stats in comp["statistiques_par_colonne"].items():
                if stats["nb_ecarts"] > 0:
                    colonnes_ecarts[col] = colonnes_ecarts.get(col, 0) + stats["nb_ecarts"]
        
        if colonnes_ecarts:
            top_colonnes = sorted(colonnes_ecarts.items(), key=lambda x: x[1], reverse=True)[:10]
            cols = [c[0] for c in top_colonnes]
            nb_ecarts = [c[1] for c in top_colonnes]
            
            axes[1, 0].barh(cols, nb_ecarts, color='#9B59B6')
            axes[1, 0].set_xlabel('Nombre d\'écarts')
            axes[1, 0].set_title('Top 10 - Colonnes avec le plus d\'écarts', fontweight='bold')
            axes[1, 0].grid(axis='x', alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'Aucun écart par colonne', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Top 10 - Colonnes avec le plus d\'écarts', fontweight='bold')
        
        # 4. Répartition par type d'écart
        types_ecarts = {}
        for comp in self.rapport["comparaisons"]:
            for ecart in comp["ecarts"]:
                t = ecart["type_ecart"]
                types_ecarts[t] = types_ecarts.get(t, 0) + 1
        
        if types_ecarts:
            labels = list(types_ecarts.keys())
            sizes = list(types_ecarts.values())
            colors = ['#E63946', '#F39C12', '#3498DB', '#2ECC71']
            
            axes[1, 1].pie(sizes, labels=labels, autopct='%1.1f%%', 
                          colors=colors[:len(labels)], startangle=90)
            axes[1, 1].set_title('Répartition par type d\'écart', fontweight='bold')
        else:
            axes[1, 1].text(0.5, 0.5, 'Aucun écart', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Répartition par type d\'écart', fontweight='bold')
        
        plt.suptitle('Analyse de la Réconciliation - MILES vs SAP', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if fichier is None:
            fichier = os.path.join("..", "docs", "reconciliation_analysis.png")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        plt.savefig(fichier, dpi=300, bbox_inches='tight')
        print(f"   💾 Graphique sauvegardé : {fichier}")
        plt.show()
        
        return fichier
    
    # ============================================================
    # 4. RAPPORT ET EXPORTS
    # ============================================================
    
    def calculer_score_reconciliation(self):
        """Calcule le score global de réconciliation"""
        if not self.rapport["comparaisons"]:
            return 0
        
        # Score basé sur :
        # - Taux de correspondance (40%)
        # - Taux d'écart critique (30%)
        # - Taux d'écart mineur (30%)
        
        taux_correspondance_moyen = np.mean([c["taux_correspondance"] for c in self.rapport["comparaisons"]])
        
        total_ecarts_critiques = self.rapport["ecarts_critiques"]
        total_ecarts = self.rapport["total_ecarts"] + 1
        taux_ecarts_critiques = (total_ecarts_critiques / total_ecarts) * 100 if total_ecarts > 0 else 0
        
        total_ecarts_mineurs = self.rapport["ecarts_mineurs"]
        taux_ecarts_mineurs = (total_ecarts_mineurs / total_ecarts) * 100 if total_ecarts > 0 else 0
        
        score = (
            taux_correspondance_moyen * 0.4 +
            (100 - taux_ecarts_critiques) * 0.3 +
            (100 - taux_ecarts_mineurs) * 0.3
        )
        
        self.rapport["score_reconciliation"] = score
        return score
    
    def afficher_rapport(self):
        """Affiche le rapport complet"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE RÉCONCILIATION")
        print("=" * 60)
        print(f"   📅 Date : {self.rapport['date_execution']}")
        print(f"   📋 Comparaisons : {len(self.rapport['comparaisons'])}")
        print(f"   📌 Total écarts : {self.rapport['total_ecarts']}")
        print(f"   🔴 Écarts critiques : {self.rapport['ecarts_critiques']}")
        print(f"   🟡 Écarts mineurs : {self.rapport['ecarts_mineurs']}")
        print(f"   📤 Manquants source : {self.rapport['manquants_source']}")
        print(f"   📥 Manquants cible : {self.rapport['manquants_cible']}")
        
        # Score global
        score = self.calculer_score_reconciliation()
        print(f"\n   🎯 SCORE DE RÉCONCILIATION : {score:.1f}/100")
        
        if score >= 90:
            print(f"      ✅ Excellent - Données cohérentes")
        elif score >= 70:
            print(f"      🟡 Acceptable - Quelques écarts à corriger")
        else:
            print(f"      ❌ Critique - Nombreux écarts détectés")
        
        # Détail par table
        for comp in self.rapport['comparaisons']:
            print(f"\n   📋 Table {comp['table']} :")
            print(f"      - Taux correspondance : {comp['taux_correspondance']:.1f}%")
            print(f"      - Écarts : {comp['nb_ecarts']} (dont {comp['nb_ecarts_critiques']} critiques)")
            
            if comp['ecarts']:
                print(f"      - Top 5 écarts :")
                for ecart in comp['ecarts'][:5]:
                    critique = "🔴" if ecart['critique'] else "🟡"
                    print(f"         {critique} {ecart['colonne']} : {ecart['valeur_source']} → {ecart['valeur_cible']}")
    
    def exporter_rapport_json(self, fichier=None):
        """Exporte le rapport au format JSON"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "rapport_reconciliation.json")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(self.rapport, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   💾 Rapport JSON exporté : {fichier}")
        return fichier
    
    def exporter_rapport_excel(self, fichier=None):
        """Exporte le rapport au format Excel avec plusieurs feuilles"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "rapport_reconciliation.xlsx")
        
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        
        with pd.ExcelWriter(fichier, engine='openpyxl') as writer:
            # Feuille 1 : Résumé
            resume = pd.DataFrame([{
                "Date": self.rapport['date_execution'],
                "Version": self.rapport['version'],
                "Comparaisons": len(self.rapport['comparaisons']),
                "Total écarts": self.rapport['total_ecarts'],
                "Écarts critiques": self.rapport['ecarts_critiques'],
                "Écarts mineurs": self.rapport['ecarts_mineurs'],
                "Manquants source": self.rapport['manquants_source'],
                "Manquants cible": self.rapport['manquants_cible'],
                "Score réconciliation": f"{self.calculer_score_reconciliation():.1f}/100"
            }])
            resume.to_excel(writer, sheet_name='Résumé', index=False)
            
            # Feuille 2 : Détail des écarts
            tous_ecarts = []
            for comp in self.rapport['comparaisons']:
                for ecart in comp['ecarts']:
                    tous_ecarts.append({
                        "Table": comp['table'],
                        "Clé": ecart['cle_valeur'],
                        "Colonne": ecart['colonne'],
                        "Valeur source": ecart['valeur_source'],
                        "Valeur cible": ecart['valeur_cible'],
                        "Type": ecart['type_ecart'],
                        "Critique": "Oui" if ecart['critique'] else "Non"
                    })
            
            if tous_ecarts:
                df_ecarts = pd.DataFrame(tous_ecarts)
                df_ecarts.to_excel(writer, sheet_name='Écarts', index=False)
            
            # Feuille 3 : Statistiques par colonne
            stats_colonnes = []
            for comp in self.rapport['comparaisons']:
                for col, stats in comp['statistiques_par_colonne'].items():
                    stats_colonnes.append({
                        "Table": comp['table'],
                        "Colonne": col,
                        "Nb écarts": stats['nb_ecarts'],
                        "Critique": "Oui" if stats['critique'] else "Non"
                    })
            
            if stats_colonnes:
                df_stats = pd.DataFrame(stats_colonnes)
                df_stats.to_excel(writer, sheet_name='Statistiques_Colonnes', index=False)
            
            # Feuille 4 : Recommandations
            recommandations = []
            for comp in self.rapport['comparaisons']:
                for reco in comp.get('recommandations', []):
                    recommandations.append({
                        "Table": comp['table'],
                        "Priorité": reco['priorite'],
                        "Catégorie": reco['categorie'],
                        "Message": reco['message']
                    })
            
            if recommandations:
                df_reco = pd.DataFrame(recommandations)
                df_reco.to_excel(writer, sheet_name='Recommandations', index=False)
        
        print(f"   💾 Rapport Excel exporté : {fichier}")
        return fichier


# ============================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MOTEUR DE RÉCONCILIATION AVANCÉ - SPRINT 3 - E5")
    print("=" * 60)
    
    # 1. Créer des données de test (source MILES vs cible SAP)
    print("\n📊 Création des données de test...")
    
    # SOURCE (MILES) - 50 enregistrements
    np.random.seed(42)
    n = 50
    
    source_data = {
        "contract_id": list(range(1, n+1)),
        "reference": [f"REF{i:03d}" for i in range(1, n+1)],
        "amount": np.random.normal(20000, 5000, n).round(2),
        "status": np.random.choice(["ACTIF", "CLOTURE", "RESILIE"], n),
        "customer_name": [f"Client {chr(65+i%26)}" for i in range(n)],
        "credit_score": np.random.normal(700, 80, n).round(0)
    }
    df_source = pd.DataFrame(source_data)
    
    # CIBLE (SAP) - avec écarts volontaires
    cible_data = source_data.copy()
    df_cible = pd.DataFrame(cible_data)
    
    # Ajouter des écarts
    df_cible.loc[5, 'amount'] = 21000.50  # Écart de montant
    df_cible.loc[10, 'status'] = "ACTIF"  # Statut changé
    df_cible.loc[15, 'customer_name'] = "Client Modifié"  # Nom modifié
    df_cible.loc[20, 'credit_score'] = 650  # Score modifié
    df_cible.loc[25, 'amount'] = 30000.00  # Écart important
    
    # Supprimer 2 enregistrements (manquants dans la cible)
    df_cible = df_cible.drop([30, 31]).reset_index(drop=True)
    
    # Ajouter 2 enregistrements en trop (manquants dans la source)
    df_cible = pd.concat([df_cible, pd.DataFrame({
        "contract_id": [51, 52],
        "reference": ["REF051", "REF052"],
        "amount": [25000, 30000],
        "status": ["ACTIF", "ACTIF"],
        "customer_name": ["Client Z", "Client Y"],
        "credit_score": [700, 720]
    })], ignore_index=True)
    
    print(f"   ✅ Source (MILES) : {len(df_source)} enregistrements")
    print(f"   ✅ Cible (SAP) : {len(df_cible)} enregistrements")
    
    # 2. Initialiser le moteur
    engine = ReconciliationEngine()
    
    # 3. Exécuter la réconciliation
    tolerances = {"amount": 0.01, "credit_score": 5}
    colonnes_critiques = ["REFERENCE", "CONTRACT_ID", "AMOUNT"]
    
    resultat = engine.comparer(
        table_name="CONTRACT",
        source_data=df_source,
        cible_data=df_cible,
        cle="contract_id",
        tolerances=tolerances,
        colonnes_critiques=colonnes_critiques
    )
    
    # 4. Afficher le rapport
    engine.afficher_rapport()
    
    # 5. Générer les visualisations
    engine.visualiser_ecarts()
    
    # 6. Exporter les rapports
    engine.exporter_rapport_json()
    engine.exporter_rapport_excel()
    
    print("\n" + "=" * 60)
    print("🏁 FIN - Prochaine étape : E6 - Scoring")
    print("=" * 60)