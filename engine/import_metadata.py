import pandas as pd
import os
import json
from models import (
    Table, Colonne, ObjetMetier, Mapping, 
    Contrainte, Regle, ValeurReference, Ponderation,
    Referentiel
)

# ============================================================
# FONCTION UTILITAIRE : Nettoyer les noms de colonnes
# ============================================================
def nettoyer_nom_colonne(nom):
    """Nettoie un nom de colonne pour éviter les erreurs de casse"""
    if nom is None:
        return None
    return str(nom).strip().upper().replace(' ', '_')

def trouver_colonne(df, noms_possibles):
    """Trouve une colonne dans un DataFrame parmi plusieurs noms possibles"""
    colonnes_normalisees = {nettoyer_nom_colonne(col): col for col in df.columns}
    
    for nom in noms_possibles:
        nom_nettoye = nettoyer_nom_colonne(nom)
        if nom_nettoye in colonnes_normalisees:
            return colonnes_normalisees[nom_nettoye]
    
    # Si aucune colonne n'est trouvée, afficher les colonnes disponibles
    print(f"⚠️ Colonnes disponibles : {list(df.columns)}")
    return None

print("=" * 60)
print("🚀 DÉMARRAGE DU MOTEUR D'IMPORT DES MÉTADONNÉES")
print("=" * 60)
print(f"📍 SPRINT 2 - Module E2")
print("=" * 60)

# 1. Définir le chemin du fichier de métadonnées
chemin_excel = os.path.join("..", "metadata", "mon_referentiel.xlsx")
print(f"\n📁 Recherche du fichier : {chemin_excel}")

try:
    # 2. Lire TOUS les onglets du fichier Excel
    df_modele = pd.read_excel(chemin_excel, sheet_name="Modele_donnees")
    df_objets = pd.read_excel(chemin_excel, sheet_name="Objets_metier")
    df_mappings = pd.read_excel(chemin_excel, sheet_name="Mappings")
    df_contraintes = pd.read_excel(chemin_excel, sheet_name="Contraintes")
    df_regles = pd.read_excel(chemin_excel, sheet_name="Regles")
    df_valeurs = pd.read_excel(chemin_excel, sheet_name="Valeurs_reference")
    df_ponderation = pd.read_excel(chemin_excel, sheet_name="Ponderation_Score")
    
    print("\n✅ Lecture du fichier réussie !")
    print(f"   📋 'Modele_donnees'       : {len(df_modele)} lignes")
    print(f"   📋 'Objets_metier'        : {len(df_objets)} lignes")
    print(f"   📋 'Mappings'             : {len(df_mappings)} lignes")
    print(f"   📋 'Contraintes'          : {len(df_contraintes)} lignes")
    print(f"   📋 'Regles'               : {len(df_regles)} lignes")
    print(f"   📋 'Valeurs_reference'    : {len(df_valeurs)} lignes")
    print(f"   📋 'Ponderation_Score'    : {len(df_ponderation)} lignes")
    
    # ============================================================
    # 3. TRANSFORMER LES DONNÉES EN OBJETS PYTHON
    #    TÂCHE : E2-2-T1
    # ============================================================
    
    print("\n" + "=" * 60)
    print("🔧 TRANSFORMATION EN OBJETS PYTHON (E2-2-T1)")
    print("=" * 60)
    
    # Créer le conteneur principal
    referentiel = Referentiel()
    
    # 3.1 Créer les objets Table et Colonne
    for index, row in df_modele.iterrows():
        nom_table = row['TABLE_NAME']
        nom_colonne = row['COLUMN_NAME']
        type_donnee = row['DATA_TYPE']
        
        if nom_table not in referentiel.tables:
            referentiel.tables[nom_table] = Table(nom_table)
        
        referentiel.tables[nom_table].ajouter_colonne(nom_colonne, type_donnee)
    
    print(f"\n📊 {len(referentiel.tables)} tables créées :")
    for table in referentiel.tables.values():
        print(f"   - {table}")
    
    # 3.2 Créer les objets ObjetMetier
    for index, row in df_objets.iterrows():
        objet = ObjetMetier(
            row['OBJET_NOM'],
            row['TABLE_ASSOCIEE'],
            row['COLONNE_ASSOCIEE']
        )
        referentiel.objets_metier.append(objet)
    
    print(f"\n📋 {len(referentiel.objets_metier)} objets métier créés :")
    for objet in referentiel.objets_metier:
        print(f"   - {objet}")
    
    # 3.3 Créer les objets Mapping
    for index, row in df_mappings.iterrows():
        mapping = Mapping(
            row['SYSTEME_SOURCE'],
            row['TABLE_SOURCE'],
            row['CHAMP_SOURCE'],
            row['SYSTEME_CIBLE'],
            row['TABLE_CIBLE'],
            row['CHAMP_CIBLE']
        )
        referentiel.mappings.append(mapping)
    
    print(f"\n🔗 {len(referentiel.mappings)} mappings créés :")
    for mapping in referentiel.mappings:
        print(f"   - {mapping}")
    
    # 3.4 Créer les objets Contrainte
    print("\n🔒 Création des contraintes...")
    
    col_table = trouver_colonne(df_contraintes, ['TABLE_NAME', 'TABLE', 'NOM_TABLE'])
    col_colonne = trouver_colonne(df_contraintes, ['COLUMN_NAME', 'COLONNE', 'NOM_COLONNE'])
    col_type = trouver_colonne(df_contraintes, ['TYPE_CONTRAINTE', 'TYPE_DE_CONTRAINTE', 'CONTRAINTE_TYPE', 'TYPE'])
    col_valeur = trouver_colonne(df_contraintes, ['VALEUR', 'VALUE'])
    
    if col_table and col_colonne and col_type:
        for index, row in df_contraintes.iterrows():
            contrainte = Contrainte(
                row[col_table],
                row[col_colonne],
                row[col_type],
                row[col_valeur] if col_valeur else None
            )
            referentiel.contraintes.append(contrainte)
        
        print(f"✅ {len(referentiel.contraintes)} contraintes créées :")
        for contrainte in referentiel.contraintes[:5]:
            print(f"   - {contrainte}")
        if len(referentiel.contraintes) > 5:
            print(f"   ... et {len(referentiel.contraintes) - 5} autres")
    else:
        print("⚠️ Impossible de trouver les colonnes nécessaires pour les contraintes")
    
    # 3.5 Créer les objets Regle
    for index, row in df_regles.iterrows():
        regle = Regle(
            row['REGLE_ID'],
            row['NOM_REGLE'],
            row['DESCRIPTION'],
            row['EXPRESSION_SQL']
        )
        referentiel.regles.append(regle)
    
    print(f"\n📜 {len(referentiel.regles)} règles créées :")
    for regle in referentiel.regles:
        print(f"   - {regle}")
    
    # 3.6 Créer les objets ValeurReference
    for index, row in df_valeurs.iterrows():
        valeur = ValeurReference(
            row['LISTE_NOM'],
            row['CODE_VALEUR'],
            row['LIBELLE_VALEUR']
        )
        referentiel.valeurs_reference.append(valeur)
    
    print(f"\n📚 {len(referentiel.valeurs_reference)} valeurs de référence créées :")
    for valeur in referentiel.valeurs_reference[:5]:
        print(f"   - {valeur}")
    if len(referentiel.valeurs_reference) > 5:
        print(f"   ... et {len(referentiel.valeurs_reference) - 5} autres")
    
    # 3.7 Créer les objets Ponderation
    print("\n⚖️ Création des pondérations...")
    
    col_dimension = trouver_colonne(df_ponderation, ['DIMENSION', 'DIM', 'DIMENSION_SCORE', 'NOM_DIMENSION'])
    col_poids = trouver_colonne(df_ponderation, ['POIDS', 'POID', 'WEIGHT', 'VALEUR_POIDS'])
    
    if col_dimension and col_poids:
        for index, row in df_ponderation.iterrows():
            ponderation = Ponderation(
                row[col_dimension],
                row[col_poids]
            )
            referentiel.ponderations.append(ponderation)
        
        print(f"✅ {len(referentiel.ponderations)} pondérations créées :")
        for ponderation in referentiel.ponderations:
            print(f"   - {ponderation}")
    else:
        print("⚠️ Impossible de trouver les colonnes nécessaires pour les pondérations")
        print(f"   Colonnes disponibles : {list(df_ponderation.columns)}")
    
    # ============================================================
    # 4. RÉSUMÉ DE L'IMPORT
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE L'IMPORT")
    print("=" * 60)
    print(f"   Tables              : {len(referentiel.tables)}")
    print(f"   Objets métier       : {len(referentiel.objets_metier)}")
    print(f"   Mappings            : {len(referentiel.mappings)}")
    print(f"   Contraintes         : {len(referentiel.contraintes)}")
    print(f"   Règles              : {len(referentiel.regles)}")
    print(f"   Valeurs de référence: {len(referentiel.valeurs_reference)}")
    print(f"   Pondérations        : {len(referentiel.ponderations)}")
    
    # ============================================================
    # 5. SAUVEGARDE DU RÉFÉRENTIEL (E2-3)
    # ============================================================
    print("\n" + "=" * 60)
    print("💾 SAUVEGARDE DU RÉFÉRENTIEL (E2-3)")
    print("=" * 60)
    
    # Définir le chemin du fichier JSON
    chemin_json = os.path.join("..", "metadata", "referentiel.json")
    
    # Sauvegarder le référentiel
    referentiel.to_json(chemin_json)
    print(f"   ✅ Référentiel sauvegardé dans : {chemin_json}")
    
    # Vérifier la taille du fichier
    if os.path.exists(chemin_json):
        taille_fichier = os.path.getsize(chemin_json)
        print(f"   📊 Taille du fichier : {taille_fichier} octets")
    else:
        print("   ⚠️ Le fichier n'a pas été créé correctement")
    
    # ============================================================
    # 6. CHARGEMENT DU RÉFÉRENTIEL (pour vérification)
    # ============================================================
    print("\n" + "=" * 60)
    print("🔄 CHARGEMENT DU RÉFÉRENTIEL DEPUIS JSON")
    print("=" * 60)
    
    referentiel_charge = Referentiel.from_json(chemin_json)
    print(f"   ✅ Référentiel chargé avec succès !")
    print(f"   📦 Objet : {referentiel_charge}")
    
    print("\n📊 Vérification des données chargées :")
    print(f"   Tables              : {len(referentiel_charge.tables)}")
    print(f"   Objets métier       : {len(referentiel_charge.objets_metier)}")
    print(f"   Mappings            : {len(referentiel_charge.mappings)}")
    print(f"   Contraintes         : {len(referentiel_charge.contraintes)}")
    print(f"   Règles              : {len(referentiel_charge.regles)}")
    print(f"   Valeurs de référence: {len(referentiel_charge.valeurs_reference)}")
    print(f"   Pondérations        : {len(referentiel_charge.ponderations)}")
    
    # ============================================================
    # 7. AFFICHER LE CONTENU DU FICHIER JSON (extrait)
    # ============================================================
    print("\n" + "=" * 60)
    print("📄 EXTRAIT DU FICHIER JSON")
    print("=" * 60)
    
    with open(chemin_json, 'r', encoding='utf-8') as f:
        contenu = f.read()
        # Afficher les 500 premiers caractères
        if len(contenu) > 500:
            print(contenu[:500] + "\n...")
        else:
            print(contenu)

except FileNotFoundError:
    print(f"\n❌ ERREUR : Le fichier '{chemin_excel}' n'a pas été trouvé.")
    print("   Assurez-vous que le fichier existe dans le dossier 'metadata/'")
    
except Exception as e:
    print(f"\n❌ Une erreur inattendue s'est produite : {e}")
    print(f"   Détail : {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🏁 FIN DE L'IMPORT")
print("=" * 60)
print("📍 Prochaine étape : Sprint 3 - E3 Knowledge Graph")