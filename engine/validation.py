# engine/validation.py
# ============================================================
# MODULE : Moteur de validation
# SPRINT : 3
# MODULE : E4 - Moteur de validation
# TÂCHE  : E4-1 à E4-6
# ============================================================

import pandas as pd
import os
import json
from datetime import datetime
from models import Referentiel


class ValidationEngine:
    """
    Moteur de validation générique.
    Exécute les règles définies dans le référentiel sur les données.
    """
    
    def __init__(self, referentiel):
        """
        Initialise le moteur avec le référentiel
        
        Args:
            referentiel (Referentiel): Référentiel de métadonnées
        """
        self.referentiel = referentiel
        self.resultats = []
        self.rapport = {
            "date_execution": datetime.now().isoformat(),
            "total_regles": 0,
            "regles_valides": 0,
            "regles_echouees": 0,
            "anomalies": []
        }
        self._donnees = {}  # Cache pour les données chargées
    
    def charger_donnees(self, table_name, data):
        """
        Charge les données d'une table dans le cache
        
        Args:
            table_name (str): Nom de la table
            data (pd.DataFrame): Données à valider
        """
        self._donnees[table_name] = data
        print(f"   ✅ Données chargées : {table_name} ({len(data)} lignes)")
    
    def charger_donnees_depuis_csv(self, dossier="DataX"):
        """
        Charge toutes les données depuis des fichiers CSV
        
        Args:
            dossier (str): Dossier contenant les fichiers CSV
        """
        for table_name in self.referentiel.tables.keys():
            fichier = os.path.join("..", dossier, f"{table_name}.csv")
            if os.path.exists(fichier):
                df = pd.read_csv(fichier)
                self.charger_donnees(table_name, df)
            else:
                print(f"   ⚠️ Fichier non trouvé : {fichier}")
    
    def _executer_regle(self, regle):
        """
        Exécute une règle sur les données
        
        Args:
            regle (Regle): Règle à exécuter
            
        Returns:
            dict: Résultat de l'exécution
        """
        resultat = {
            "regle_id": regle.id,
            "regle_nom": regle.nom,
            "description": regle.description,
            "expression": regle.expression_sql,
            "statut": "OK",
            "nb_anomalies": 0,
            "anomalies": []
        }
        
        try:
            # Extraire le nom de la table de l'expression SQL
            table_name = self._extraire_table(regle.expression_sql)
            
            if table_name not in self._donnees:
                resultat["statut"] = "ERREUR"
                resultat["message"] = f"Table {table_name} non chargée"
                return resultat
            
            df = self._donnees[table_name]
            
            # Exécuter la requête
            # Pour simplifier, on simule l'exécution
            # Dans la vraie vie, on utiliserait une connexion SQL
            
            # Ici on simule des anomalies
            anomalies = self._simuler_validation(df, regle)
            
            if anomalies:
                resultat["statut"] = "ECHEC"
                resultat["nb_anomalies"] = len(anomalies)
                resultat["anomalies"] = anomalies
            
        except Exception as e:
            resultat["statut"] = "ERREUR"
            resultat["message"] = str(e)
        
        return resultat
    
    def _extraire_table(self, expression_sql):
        """Extrait le nom de la table d'une expression SQL"""
        mots = expression_sql.upper().split()
        for i, mot in enumerate(mots):
            if mot in ['FROM', 'JOIN'] and i + 1 < len(mots):
                table = mots[i + 1].replace(';', '').replace(',', '')
                if table in self.referentiel.tables:
                    return table
        return None
    
    def _simuler_validation(self, df, regle):
        """
        Simule la validation pour démonstration
        
        Dans la vraie vie, cette méthode exécuterait la requête SQL.
        """
        anomalies = []
        
        # Extraction du type de règle depuis l'expression
        expr = regle.expression_sql.upper()
        
        # Règle NOT NULL
        if "IS NULL" in expr and "WHERE" in expr:
            # Trouver la colonne après WHERE
            where_part = expr.split("WHERE")[1].strip()
            if "IS NULL" in where_part:
                colonne = where_part.split("IS NULL")[0].strip()
                if colonne in df.columns:
                    nb_null = df[colonne].isna().sum()
                    if nb_null > 0:
                        anomalies.append({
                            "type": "NOT_NULL",
                            "colonne": colonne,
                            "nb_anomalies": nb_null,
                            "exemple": df[df[colonne].isna()].head(3).to_dict('records')
                        })
        
        # Règle UNIQUE
        if "COUNT(*) > 1" in expr and "GROUP BY" in expr:
            group_part = expr.split("GROUP BY")[1].split("HAVING")[0].strip()
            if group_part in df.columns:
                doublons = df[group_part].value_counts()
                doublons = doublons[doublons > 1]
                if len(doublons) > 0:
                    anomalies.append({
                        "type": "UNIQUE",
                        "colonne": group_part,
                        "nb_anomalies": len(doublons),
                        "exemple": doublons.head(3).to_dict()
                    })
        
        # Règle POSITIVE (AMOUNT < 0)
        if "AMOUNT < 0" in expr:
            if "AMOUNT" in df.columns:
                nb_negatif = (df["AMOUNT"] < 0).sum()
                if nb_negatif > 0:
                    anomalies.append({
                        "type": "POSITIVE",
                        "colonne": "AMOUNT",
                        "nb_anomalies": nb_negatif,
                        "exemple": df[df["AMOUNT"] < 0].head(3).to_dict('records')
                    })
        
        # Règle FORMAT (EMAIL)
        if "NOT LIKE '%@%.%'" in expr:
            if "EMAIL" in df.columns:
                nb_invalide = (~df["EMAIL"].astype(str).str.contains('@', na=False)).sum()
                if nb_invalide > 0:
                    anomalies.append({
                        "type": "FORMAT_EMAIL",
                        "colonne": "EMAIL",
                        "nb_anomalies": nb_invalide,
                        "exemple": df[~df["EMAIL"].astype(str).str.contains('@', na=False)].head(3).to_dict('records')
                    })
        
        # Règle DATE_RANGE (END_DATE < START_DATE)
        if "END_DATE < START_DATE" in expr:
            if "END_DATE" in df.columns and "START_DATE" in df.columns:
                df_dates = df.dropna(subset=['END_DATE', 'START_DATE'])
                try:
                    # Conversion en datetime
                    df_dates['END_DATE'] = pd.to_datetime(df_dates['END_DATE'])
                    df_dates['START_DATE'] = pd.to_datetime(df_dates['START_DATE'])
                    nb_invalide = (df_dates['END_DATE'] < df_dates['START_DATE']).sum()
                    if nb_invalide > 0:
                        anomalies.append({
                            "type": "DATE_RANGE",
                            "colonne": "END_DATE",
                            "nb_anomalies": nb_invalide,
                            "exemple": df_dates[df_dates['END_DATE'] < df_dates['START_DATE']].head(3).to_dict('records')
                        })
                except:
                    pass
        
        return anomalies
    
    def executer_toutes_les_regles(self):
        """
        Exécute toutes les règles du référentiel
        
        Returns:
            dict: Rapport complet de validation
        """
        print("\n" + "=" * 60)
        print("🚀 EXÉCUTION DU MOTEUR DE VALIDATION (E4)")
        print("=" * 60)
        
        self.rapport = {
            "date_execution": datetime.now().isoformat(),
            "total_regles": len(self.referentiel.regles),
            "regles_valides": 0,
            "regles_echouees": 0,
            "regles_en_erreur": 0,
            "anomalies": []
        }
        
        for regle in self.referentiel.regles:
            print(f"\n📜 Exécution : {regle.id} - {regle.nom}")
            resultat = self._executer_regle(regle)
            self.resultats.append(resultat)
            
            if resultat["statut"] == "OK":
                self.rapport["regles_valides"] += 1
                print(f"   ✅ OK")
            elif resultat["statut"] == "ECHEC":
                self.rapport["regles_echouees"] += 1
                print(f"   ❌ ÉCHEC : {resultat['nb_anomalies']} anomalies")
                self.rapport["anomalies"].append(resultat)
            else:
                self.rapport["regles_en_erreur"] += 1
                print(f"   ⚠️ ERREUR : {resultat.get('message', 'Inconnue')}")
        
        # Afficher le résumé
        self.afficher_rapport()
        
        return self.rapport
    
    def afficher_rapport(self):
        """Affiche le rapport de validation"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE VALIDATION")
        print("=" * 60)
        print(f"   📅 Date : {self.rapport['date_execution']}")
        print(f"   📋 Règles totales : {self.rapport['total_regles']}")
        print(f"   ✅ Règles valides : {self.rapport['regles_valides']}")
        print(f"   ❌ Règles échouées : {self.rapport['regles_echouees']}")
        print(f"   ⚠️ Règles en erreur : {self.rapport['regles_en_erreur']}")
        
        if self.rapport['anomalies']:
            print(f"\n   📋 Anomalies détectées :")
            for anomalie in self.rapport['anomalies']:
                print(f"      - {anomalie['regle_id']} : {anomalie['regle_nom']}")
                print(f"        {anomalie['nb_anomalies']} anomalies")
                for a in anomalie['anomalies'][:2]:
                    print(f"          * {a['type']} : {a['nb_anomalies']}")
    
    def exporter_rapport_json(self, fichier=None):
        """Exporte le rapport au format JSON"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "rapport_validation.json")
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(self.rapport, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport exporté : {fichier}")
        return fichier


# ============================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MOTEUR DE VALIDATION - SPRINT 3 - E4")
    print("=" * 60)
    
    # 1. Charger le référentiel
    chemin_json = os.path.join("..", "metadata", "referentiel.json")
    print(f"\n📁 Chargement du référentiel : {chemin_json}")
    
    if os.path.exists(chemin_json):
        referentiel = Referentiel.from_json(chemin_json)
        print(f"   ✅ {len(referentiel.tables)} tables, {len(referentiel.regles)} règles")
        
        # 2. Créer des données de test
        print("\n📊 Création des données de test...")
        
        # Données CONTRACT
        contract_data = {
            "contract_id": [1, 2, 3, 4, 5],
            "reference": ["REF001", None, "REF003", "REF004", "REF005"],
            "start_date": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-03-01", "2024-04-01"],
            "end_date": ["2024-12-31", "2024-12-31", "2023-12-31", "2024-12-31", "2024-12-31"],
            "amount": [10000, 15000, -5000, 20000, 25000]
        }
        
        # Données CUSTOMER
        customer_data = {
            "customer_id": [1, 2, 3, 4, 5],
            "first_name": ["Jean", None, "Marie", "Sophie", "Paul"],
            "last_name": ["Dupont", "Martin", None, "Bernard", "Petit"],
            "email": ["jean@email.com", "martin@email", "marie@email.com", "sophie@email.com", None],
            "phone": ["0102030405", "0203040506", "0304050607", None, "0506070809"]
        }
        
        # Données FLEETVEHICLE
        fleet_data = {
            "fleetvehicle_id": [1, 2, 3, 4, 5],
            "license_plate": ["AB-123-CD", "DE-456-FG", None, "HI-789-JK", "LM-012-NO"],
            "vin": ["VIN001", "VIN002", "VIN003", "VIN002", "VIN005"],
            "make": ["Renault", "Peugeot", "Citroen", "Renault", "Peugeot"],
            "model": ["Clio", "208", "C3", "Megane", "3008"],
            "year": [2020, 2021, 2022, 2021, 2023]
        }
        
        # Créer les DataFrames
        df_contract = pd.DataFrame(contract_data)
        df_customer = pd.DataFrame(customer_data)
        df_fleet = pd.DataFrame(fleet_data)
        
        # 3. Initialiser le moteur de validation
        engine = ValidationEngine(referentiel)
        
        # 4. Charger les données
        engine.charger_donnees("CONTRACT", df_contract)
        engine.charger_donnees("CUSTOMER", df_customer)
        engine.charger_donnees("FLEETVEHICLE", df_fleet)
        
        # 5. Exécuter les règles
        rapport = engine.executer_toutes_les_regles()
        
        # 6. Exporter le rapport
        engine.exporter_rapport_json()
        
        print("\n" + "=" * 60)
        print("🏁 FIN - Prochaine étape : E5 - Module de réconciliation")
        print("=" * 60)
        
    else:
        print("❌ Fichier non trouvé. Exécutez d'abord import_metadata.py")