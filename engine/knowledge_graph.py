# engine/knowledge_graph.py
# ============================================================
# MODULE : Knowledge Graph - Version finale améliorée
# SPRINT : 2 - E3
# ============================================================

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
import json
import math
from models import Referentiel


class KnowledgeGraph:
    """Version avec mise en page professionnelle"""
    
    # Dictionnaire des couleurs
    COULEURS = {
        "objet_metier": "#FF6B35",   # Orange
        "table": "#0077BE",          # Bleu
        "colonne": "#2ECC71",        # Vert
        "contrainte": "#9B59B6",     # Violet
        "regle": "#E63946",          # Rouge
    }
    
    # Formes des nœuds
    FORMES = {
        "objet_metier": "o",         # Cercle
        "table": "o",                # Cercle
        "colonne": "s",              # Carré
        "contrainte": "s",           # Carré
        "regle": "o",                # Cercle
    }
    
    # Tailles des nœuds
    TAILLES = {
        "objet_metier": 2500,
        "table": 2000,
        "colonne": 1200,
        "contrainte": 900,
        "regle": 1400,
    }
    
    LEGENDE = {
        "objet_metier": "Objets métier",
        "table": "Tables MILES",
        "colonne": "Colonnes",
        "contrainte": "Contraintes",
        "regle": "Règles de validation",
    }
    
    def __init__(self, referentiel):
        self.referentiel = referentiel
        self.graph = nx.DiGraph()
        self._construire_graphe()
    
    def _construire_graphe(self):
        """Construit un graphe organisé avec des relations claires"""
        print("🔧 Construction du graphe...")
        self.graph.clear()
        
        # === NIVEAU 1 : Objets métier (Orange) ===
        for objet in self.referentiel.objets_metier:
            self.graph.add_node(
                f"OBJ_{objet.nom}",
                type="objet_metier",
                layer=0,
                label=objet.nom,
                group="metier"
            )
        
        # === NIVEAU 2 : Tables (Bleu) ===
        for nom_table in self.referentiel.tables.keys():
            self.graph.add_node(
                nom_table,
                type="table",
                layer=1,
                label=nom_table,
                group="table"
            )
            # Lien Objet métier → Table
            for objet in self.referentiel.objets_metier:
                if objet.table_associee == nom_table:
                    self.graph.add_edge(
                        f"OBJ_{objet.nom}",
                        nom_table,
                        relation="est_associe_a",
                        couleur_relation=self.COULEURS["objet_metier"]
                    )
        
        # === NIVEAU 3 : Colonnes (Vert) ===
        for nom_table, table in self.referentiel.tables.items():
            for col in table.colonnes:
                id_col = f"{nom_table}.{col.nom}"
                self.graph.add_node(
                    id_col,
                    type="colonne",
                    layer=2,
                    label=col.nom,
                    table_parent=nom_table,
                    group="colonne"
                )
                # Lien Table → Colonne (Bleu)
                self.graph.add_edge(
                    nom_table,
                    id_col,
                    relation="contient",
                    couleur_relation=self.COULEURS["table"]
                )
        
        # === NIVEAU 4 : Contraintes (Violet) ===
        for c in self.referentiel.contraintes:
            id_cont = f"{c.table_name}.{c.colonne_name}.{c.type_contrainte}"
            self.graph.add_node(
                id_cont,
                type="contrainte",
                layer=3,
                label=c.type_contrainte,
                type_complet=c.type_contrainte,
                table_parent=c.table_name,
                colonne_parent=c.colonne_name,
                group="contrainte"
            )
            # Lien Colonne → Contrainte (Vert)
            id_col = f"{c.table_name}.{c.colonne_name}"
            if id_col in self.graph:
                self.graph.add_edge(
                    id_col,
                    id_cont,
                    relation="a_contrainte",
                    couleur_relation=self.COULEURS["colonne"]
                )
        
        # === NIVEAU 5 : Règles (Rouge) ===
        for r in self.referentiel.regles:
            self.graph.add_node(
                r.id,
                type="regle",
                layer=4,
                label=r.id,
                nom_complet=r.nom,
                description=r.description,
                group="regle"
            )
            # Lien Règle → Table (Rouge)
            tables = self._extraire_tables(r.expression_sql)
            for t in tables:
                if t in self.graph:
                    self.graph.add_edge(
                        r.id,
                        t,
                        relation="valide",
                        couleur_relation=self.COULEURS["regle"]
                    )
        
        print(f"✅ {len(self.graph.nodes)} nœuds, {len(self.graph.edges)} relations")
    
    def _extraire_tables(self, sql):
        """Extrait les noms de tables d'une requête SQL"""
        tables = []
        mots = sql.upper().replace('(', ' ').replace(')', ' ').split()
        for i, mot in enumerate(mots):
            if mot in ['FROM', 'JOIN'] and i + 1 < len(mots):
                table = mots[i + 1].replace(';', '').replace(',', '')
                if table in self.referentiel.tables:
                    tables.append(table)
        return tables
    
    def _position_par_groupes(self):
        """Positionne les nœuds par groupes avec le bon espacement"""
        pos = {}
        
        # Séparer les nœuds par groupe
        groupes = {
            "metier": [],
            "table": [],
            "colonne": [],
            "contrainte": [],
            "regle": []
        }
        
        for node, attrs in self.graph.nodes(data=True):
            group = attrs.get('group', 'unknown')
            if group in groupes:
                groupes[group].append(node)
        
        # Positionner les couches verticalement avec espacement
        y_positions = {
            "metier": 5.0,
            "table": 3.5,
            "colonne": 2.0,
            "contrainte": 0.5,
            "regle": -1.5
        }
        
        # Espacement horizontal par couche
        for group, nodes in groupes.items():
            y = y_positions.get(group, 0)
            n = len(nodes)
            if n == 0:
                continue
            
            # Espacement adaptatif selon le nombre de nœuds
            if n <= 3:
                spacing_x = 4.0
            elif n <= 6:
                spacing_x = 3.0
            else:
                spacing_x = 2.5
            
            for i, node in enumerate(nodes):
                x = (i - (n - 1) / 2) * spacing_x
                pos[node] = (x, y)
        
        # Ajuster les positions verticalement selon le type
        # Pour éviter les chevauchements entre les couches
        return pos
    
    def visualiser(self, fichier=None, figsize=(20, 16)):
        """Visualisation avec mise en page professionnelle"""
        print("\n📊 Génération de la visualisation...")
        
        fig, ax = plt.subplots(figsize=figsize)
        pos = self._position_par_groupes()
        
        # === 1. DESSINER LES ARÊTES AVEC COULEURS ===
        for source, target, attrs in self.graph.edges(data=True):
            color = attrs.get('couleur_relation', '#888888')
            # Flèches plus épaisses et visibles
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=[(source, target)],
                edge_color=color,
                arrows=True,
                arrowsize=20,
                arrowstyle='->',
                alpha=0.7,
                width=2.0,
                ax=ax
            )
        
        # === 2. DESSINER LES NŒUDS PAR TYPE ===
        nodes_by_type = {
            "objet_metier": [],
            "table": [],
            "colonne": [],
            "contrainte": [],
            "regle": []
        }
        
        for node, attrs in self.graph.nodes(data=True):
            typ = attrs.get('type', 'unknown')
            if typ in nodes_by_type:
                nodes_by_type[typ].append(node)
        
        for typ, nodes in nodes_by_type.items():
            if nodes:
                color = self.COULEURS.get(typ, '#999999')
                shape = self.FORMES.get(typ, 'o')
                size = self.TAILLES.get(typ, 1200)
                
                nx.draw_networkx_nodes(
                    self.graph, pos,
                    nodelist=nodes,
                    node_color=color,
                    node_shape=shape,
                    node_size=size,
                    alpha=0.9,
                    edgecolors='white',
                    linewidths=2,
                    ax=ax
                )
        
        # === 3. DESSINER LES ÉTIQUETTES ===
        labels = {}
        for node, attrs in self.graph.nodes(data=True):
            label = attrs.get('label', node)
            # Tronquer les labels trop longs
            if len(label) > 15:
                label = label[:12] + '...'
            labels[node] = label
        
        # Taille de police adaptative
        font_size = 8
        if len(self.graph.nodes) > 50:
            font_size = 6
        elif len(self.graph.nodes) > 30:
            font_size = 7
        
        nx.draw_networkx_labels(
            self.graph, pos,
            labels=labels,
            font_size=font_size,
            font_weight='bold',
            ax=ax
        )
        
        # === 4. LÉGENDE ===
        legend_elements = []
        for typ, color in self.COULEURS.items():
            label = self.LEGENDE.get(typ, typ)
            shape = self.FORMES.get(typ, 'o')
            if shape == 's':
                legend_elements.append(
                    Patch(facecolor=color, edgecolor='white', label=label, linewidth=2)
                )
            else:
                legend_elements.append(
                    Patch(facecolor=color, edgecolor='white', label=label, linewidth=2)
                )
        
        ax.legend(
            handles=legend_elements,
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            title="Légende",
            fontsize=12,
            title_fontsize=13
        )
        
        # === 5. TITRE ET FORMAT ===
        ax.set_title(
            "Knowledge Graph - Référentiel MILES\n"
            "Objets métier (Orange) → Tables (Bleu) → Colonnes (Vert) → Contraintes (Violet) → Règles (Rouge)",
            fontsize=14,
            fontweight='bold'
        )
        ax.axis('off')
        plt.tight_layout()
        
        # === 6. SAUVEGARDE ===
        if fichier is None:
            fichier = os.path.join("..", "docs", "knowledge_graph.png")
        
        # Sauvegarde haute résolution
        plt.savefig(fichier, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Image sauvegardée : {fichier}")
        
        # Sauvegarde PDF vectoriel (parfait pour la soutenance)
        fichier_pdf = fichier.replace('.png', '.pdf')
        plt.savefig(fichier_pdf, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ PDF vectoriel sauvegardé : {fichier_pdf}")
        
        plt.show()
        return fichier
    
    def afficher_statistiques(self):
        """Affiche les statistiques détaillées"""
        print("\n" + "=" * 60)
        print("📊 STATISTIQUES DU KNOWLEDGE GRAPH")
        print("=" * 60)
        print(f"   Nœuds : {len(self.graph.nodes)}")
        print(f"   Relations : {len(self.graph.edges)}")
        
        types = {}
        for node, attrs in self.graph.nodes(data=True):
            typ = attrs.get('type', 'unknown')
            types[typ] = types.get(typ, 0) + 1
        
        print("\n   Répartition par type :")
        for typ, count in types.items():
            label = self.LEGENDE.get(typ, typ)
            print(f"      - {label} : {count}")
    
    def exporter_json(self, fichier=None):
        """Exporte le graphe en JSON"""
        if fichier is None:
            fichier = os.path.join("..", "docs", "knowledge_graph.json")
        
        data = {"nodes": [], "edges": []}
        for node, attrs in self.graph.nodes(data=True):
            data["nodes"].append({
                "id": node,
                "type": attrs.get('type'),
                "label": attrs.get('label')
            })
        for src, dst, attrs in self.graph.edges(data=True):
            data["edges"].append({
                "source": src,
                "target": dst,
                "relation": attrs.get('relation')
            })
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON exporté : {fichier}")
        return fichier


# ============================================================
# POINT D'ENTRÉE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 KNOWLEDGE GRAPH - SPRINT 2 - E3")
    print("=" * 60)
    
    chemin_json = os.path.join("..", "metadata", "referentiel.json")
    print(f"\n📁 Chargement : {chemin_json}")
    
    if os.path.exists(chemin_json):
        referentiel = Referentiel.from_json(chemin_json)
        kg = KnowledgeGraph(referentiel)
        
        kg.afficher_statistiques()
        kg.visualiser()
        kg.exporter_json()
        
        print("\n" + "=" * 60)
        print("🏁 FIN - Prochaine étape : Sprint 3 - E4 Moteur de validation")
    else:
        print("❌ Fichier non trouvé. Exécutez d'abord import_metadata.py")