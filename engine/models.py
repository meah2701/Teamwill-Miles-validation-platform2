# engine/models.py
# ============================================================
# MODULE : Modèles de données pour le référentiel MILES
# SPRINT : 2
# MODULE : E2 - Moteur d'import
# TÂCHE  : E2-2-T1 - Transformer les métadonnées en objets Python
# ============================================================

import json


class Table:
    """Représente une table du modèle de données MILES"""
    def __init__(self, nom, colonnes=None):
        self.nom = nom
        self.colonnes = colonnes or []
    
    def ajouter_colonne(self, nom_colonne, type_donnee):
        """Ajoute une colonne à la table"""
        self.colonnes.append(Colonne(nom_colonne, type_donnee))
    
    def __repr__(self):
        return f"Table(nom='{self.nom}', nb_colonnes={len(self.colonnes)})"


class Colonne:
    """Représente une colonne d'une table"""
    def __init__(self, nom, type_donnee):
        self.nom = nom
        self.type_donnee = type_donnee
    
    def __repr__(self):
        return f"Colonne(nom='{self.nom}', type='{self.type_donnee}')"


class ObjetMetier:
    """Représente un objet métier (ex: Contrat, Client, Véhicule)"""
    def __init__(self, nom, table_associee, colonne_associee):
        self.nom = nom
        self.table_associee = table_associee
        self.colonne_associee = colonne_associee
    
    def __repr__(self):
        return f"ObjetMetier(nom='{self.nom}', table='{self.table_associee}')"


class Mapping:
    """Représente un mapping source → cible"""
    def __init__(self, systeme_source, table_source, champ_source, 
                 systeme_cible, table_cible, champ_cible):
        self.systeme_source = systeme_source
        self.table_source = table_source
        self.champ_source = champ_source
        self.systeme_cible = systeme_cible
        self.table_cible = table_cible
        self.champ_cible = champ_cible
    
    def __repr__(self):
        return f"Mapping(source='{self.table_source}.{self.champ_source}')"


class Contrainte:
    """Représente une contrainte technique sur une colonne"""
    def __init__(self, table_name, colonne_name, type_contrainte, valeur=None):
        self.table_name = table_name
        self.colonne_name = colonne_name
        self.type_contrainte = type_contrainte
        self.valeur = valeur
    
    def __repr__(self):
        return f"Contrainte(table='{self.table_name}', col='{self.colonne_name}', type='{self.type_contrainte}')"


class Regle:
    """Représente une règle métier (validation)"""
    def __init__(self, id, nom, description, expression_sql):
        self.id = id
        self.nom = nom
        self.description = description
        self.expression_sql = expression_sql
    
    def __repr__(self):
        return f"Regle(id='{self.id}', nom='{self.nom}')"


class ValeurReference:
    """Représente une valeur de référence (liste de codes)"""
    def __init__(self, liste_nom, code_valeur, libelle_valeur):
        self.liste_nom = liste_nom
        self.code_valeur = code_valeur
        self.libelle_valeur = libelle_valeur
    
    def __repr__(self):
        return f"ValeurReference(liste='{self.liste_nom}', code='{self.code_valeur}')"


class Ponderation:
    """Représente une pondération pour le score de qualité"""
    def __init__(self, dimension, poids):
        self.dimension = dimension
        self.poids = poids
    
    def __repr__(self):
        return f"Ponderation(dimension='{self.dimension}', poids={self.poids})"


class Referentiel:
    """Conteneur principal qui agrège toutes les métadonnées"""
    def __init__(self):
        self.tables = {}
        self.objets_metier = []
        self.mappings = []
        self.contraintes = []
        self.regles = []
        self.valeurs_reference = []
        self.ponderations = []
        self.mappings_xgboost = []  # Ajout pour XGBoost

    def __repr__(self):
        return (f"Referentiel(\n"
                f"  tables={len(self.tables)},\n"
                f"  objets_metier={len(self.objets_metier)},\n"
                f"  mappings={len(self.mappings)},\n"
                f"  contraintes={len(self.contraintes)},\n"
                f"  regles={len(self.regles)},\n"
                f"  valeurs_reference={len(self.valeurs_reference)},\n"
                f"  ponderations={len(self.ponderations)}\n"
                f")")
    
    def to_dict(self):
        """Convertit le référentiel en dictionnaire pour la sérialisation JSON"""
        return {
            "tables": {
                nom: {
                    "nom": table.nom,
                    "colonnes": [
                        {"nom": col.nom, "type_donnee": col.type_donnee}
                        for col in table.colonnes
                    ]
                }
                for nom, table in self.tables.items()
            },
            "objets_metier": [
                {
                    "nom": obj.nom,
                    "table_associee": obj.table_associee,
                    "colonne_associee": obj.colonne_associee
                }
                for obj in self.objets_metier
            ],
            "mappings": [
                {
                    "systeme_source": m.systeme_source,
                    "table_source": m.table_source,
                    "champ_source": m.champ_source,
                    "systeme_cible": m.systeme_cible,
                    "table_cible": m.table_cible,
                    "champ_cible": m.champ_cible
                }
                for m in self.mappings
            ],
            "contraintes": [
                {
                    "table_name": c.table_name,
                    "colonne_name": c.colonne_name,
                    "type_contrainte": c.type_contrainte,
                    "valeur": c.valeur
                }
                for c in self.contraintes
            ],
            "regles": [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "description": r.description,
                    "expression_sql": r.expression_sql
                }
                for r in self.regles
            ],
            "valeurs_reference": [
                {
                    "liste_nom": v.liste_nom,
                    "code_valeur": v.code_valeur,
                    "libelle_valeur": v.libelle_valeur
                }
                for v in self.valeurs_reference
            ],
            "ponderations": [
                {
                    "dimension": p.dimension,
                    "poids": p.poids
                }
                for p in self.ponderations
            ]
        }
    
    def to_json(self, fichier_destination):
        """Sauvegarde le référentiel au format JSON"""
        import json
        with open(fichier_destination, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return fichier_destination
    
    @classmethod
    def from_json(cls, fichier_source):
        """Charge un référentiel depuis un fichier JSON"""
        import json
        with open(fichier_source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        referentiel = cls()
        
        # 1. Charger les tables (clé: "Modele_donnees")
        for item in data.get("Modele_donnees", []):
            nom_table = item.get("TABLE_NAME")
            nom_colonne = item.get("COLUMN_NAME")
            type_donnee = item.get("DATA_TYPE")
            
            if nom_table not in referentiel.tables:
                referentiel.tables[nom_table] = Table(nom_table)
            referentiel.tables[nom_table].ajouter_colonne(nom_colonne, type_donnee)
        
        # 2. Charger les objets métier (clé: "Objets_metier")
        for item in data.get("Objets_metier", []):
            referentiel.objets_metier.append(
                ObjetMetier(
                    item.get("OBJET_NOM"),
                    item.get("TABLE_ASSOCIEE"),
                    item.get("COLONNE_ASSOCIEE")
                )
            )
        
        # 3. Charger les mappings (clé: "Mappings")
        for item in data.get("Mappings", []):
            referentiel.mappings.append(
                Mapping(
                    item.get("SYSTEME_SOURCE"),
                    item.get("TABLE_SOURCE"),
                    item.get("CHAMP_SOURCE"),
                    item.get("SYSTEME_CIBLE"),
                    item.get("TABLE_CIBLE"),
                    item.get("CHAMP_CIBLE")
                )
            )
        
        # 4. Charger les contraintes (clé: "Contraintes")
        for item in data.get("Contraintes", []):
            referentiel.contraintes.append(
                Contrainte(
                    item.get("TABLE_NAME"),
                    item.get("COLUMN_NAME"),
                    item.get("TYPE_CONTRAINTE"),
                    item.get("VALEUR")
                )
            )
        
        # 5. Charger les règles (clé: "Regles")
        for item in data.get("Regles", []):
            referentiel.regles.append(
                Regle(
                    item.get("REGLE_ID"),
                    item.get("NOM_REGLE"),
                    item.get("DESCRIPTION"),
                    item.get("EXPRESSION_SQL")
                )
            )
        
        # 6. Charger les valeurs de référence (clé: "Valeurs_reference")
        for item in data.get("Valeurs_reference", []):
            referentiel.valeurs_reference.append(
                ValeurReference(
                    item.get("LISTE_NOM"),
                    item.get("CODE_VALEUR"),
                    item.get("LIBELLE_VALEUR")
                )
            )
        
        # 7. Charger les pondérations (clé: "Ponderation_Score")
        for item in data.get("Ponderation_Score", []):
            referentiel.ponderations.append(
                Ponderation(
                    item.get("DIMENSION"),
                    item.get("POIDS")
                )
            )
        
        # 8. Charger les mappings XGBoost (clé: "Mappings_XGBoost_Features")
        for item in data.get("Mappings_XGBoost_Features", []):
            referentiel.mappings_xgboost.append({
                "feature": item.get("Feature"),
                "table_miles": item.get("Table_MILES"),
                "colonne_miles": item.get("Colonne_MILES"),
                "type": item.get("Type"),
                "cle_jointure": item.get("Cle_jointure"),
                "justification": item.get("Justification")
            })
        
        return referentiel