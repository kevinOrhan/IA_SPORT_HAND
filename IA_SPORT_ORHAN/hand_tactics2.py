import json
import numpy as np
import pandas as pd 
#from tslearn.metrics import dtw #type: ignore 

# ==========================================
# 1. CONSTANTES ET CONFIGURATION
# ==========================================

CHEMIN_FICHIER = "data_handball/15_01_16_France_Mens_Handball_v_CzechRepublic_Mens_Handball.json"
EQUIPE_CIBLE = "France"
EQUIPE_ADVERSE = "CzechRepublic"
LIGNE_MEDIANE_X = 0

# MODÈLE THÉORIQUE "YUGO" et "YAGO" (pour le calcul de distance DTW)
MODELE_YUGO_DISTANCE = np.array([300, 250, 200, 150, 120, 100, 120, 150, 200, 250, 300])
MODELE_YAGO_DISTANCE = np.array([600, 500, 400, 300, 200, 300, 400])

SCHEMAS_TACTIQUES = {
    "Yugo_Gauche": {
        "description": "Croisé Demi-Centre / Arrière Gauche",
        "modele_dtw": MODELE_YUGO_DISTANCE,
        "roles_requis": ["DC", "ARG"], 
        "etapes": [
            {
                "id": 1, "nom": "Approche & Placement", "duree_max": 5.0, 
                "conditions": { 
                    "proximite": {"joueurs": ["DC", "ARG"], "distance_max": 800},
                    "position_absolue": {"role": "DC", "coords": [500, 0], "seuil": 400}
                }
            },
            {
                "id": 2, "nom": "Croisé", "duree_max": 2.5, 
                "conditions": {
                    "proximite": {"joueurs": ["DC", "ARG"], "distance_max": 250}, 
                    "intervalle": {"joueurs_cibles": ["DC", "ARG"], "seuil_profondeur": 250} 
                }
            }
        ]
    },
    "Yugo_Droit": {
        "description": "Croisé Demi-Centre / Arrière Droit",
        "modele_dtw": MODELE_YUGO_DISTANCE,
        "roles_requis": ["DC", "ARD"], 
        "etapes": [
            {
                "id": 1, "nom": "Approche & Placement", "duree_max": 5.0,
                "conditions": { 
                    "proximite": {"joueurs": ["DC", "ARD"], "distance_max": 800},
                    "position_absolue": {"role": "DC", "coords": [500, 0], "seuil": 400}
                }
            },
            {
                "id": 2, "nom": "Croisé", "duree_max": 2.5,
                "conditions": {
                    "proximite": {"joueurs": ["DC", "ARD"], "distance_max": 250},
                    "intervalle": {"joueurs_cibles": ["DC", "ARD"], "seuil_profondeur": 250}
                }
            }
        ]
    },
    "Yago": {
        "description": "Sortie de Pivot en poste vers 9m + Croisé DC",
        "modele_dtw": MODELE_YAGO_DISTANCE,
        "roles_requis": ["PVT", "DC"], 
        "etapes": [
            {
                "id": 1, "nom": "Sortie du Pivot (vers 9m)", "duree_max": 4.0, 
                "conditions": { 
                    "position_absolue": {"role": "PVT", "coords": [1100, 0], "seuil": 350},
                    "proximite": {"joueurs": ["PVT", "DC"], "distance_max": 900}
                }
            },
            {
                "id": 2, "nom": "Croisé / Bloc", "duree_max": 2.5, 
                "conditions": {
                    "proximite": {"joueurs": ["PVT", "DC"], "distance_max": 200}, 
                    "intervalle": {"joueurs_cibles": ["DC"], "seuil_profondeur": 250} 
                }
            }
        ]
    },
    "Espagnole_Ailier": {
        "description": "Ecran DC > Rentrée ALG > Passe ARG",
        "roles_requis": ["DC", "ALG", "ARG"], 
        "modele_dtw": MODELE_YUGO_DISTANCE, 
        "etapes": [
            {
                "id": 1, "nom": "Approche", "duree_max": 4.0, 
                "conditions": { 
                    "position_absolue": {"role": "DC", "coords": [900, 200], "seuil": 700},
                    "proximite": {"joueurs": ["DC", "ALG"], "distance_max": 1500}
                }
            },
            {
                "id": 2, "nom": "Croisé Strict", "duree_max": 3.0, 
                "conditions": {
                    "proximite": {"joueurs": ["DC", "ALG"], "distance_max": 350},
                    "position_absolue": {"role": "ALG", "coords": [1000, 200], "seuil": 500}
                }
            },
            {
                "id": 3, "nom": "Décalage sur ARG", "duree_max": 2.5,
                "conditions": {
                    "proximite": {"joueurs": ["ALG", "ARG"], "distance_max": 300},
                    "intervalle": {"joueurs_cibles": ["ARG"], "seuil_profondeur": 200}
                }
            }
        ]
    },
    "Entree_ALG_2Pivots": {
        "description": "Rentrée ALG > Attaque Ext. ARD sur Bloc > Renversement ARG",
        "roles_requis": ["ARD", "PVT", "ALG", "ARG"], 
        "modele_dtw": MODELE_YUGO_DISTANCE,
        "etapes": [
            {
                "id": 1, "nom": "Rentrée de l'Ailier (Transformation)", "duree_max": 6.0, 
                "conditions": { 
                    "position_absolue": {"role": "ALG", "coords": [1100, 200], "seuil": 700},
                    "position_absolue": {"role": "ARD", "coords": [1300, -500], "seuil": 600}
                }
            },
            {
                "id": 2, "nom": "Attaque Externe ARD & Bloc", "duree_max": 4.0, 
                "conditions": {
                    "position_absolue": {"role": "ARD", "coords": [1200, -700], "seuil": 600},
                    "proximite": {"joueurs": ["ARD", "PVT"], "distance_max": 300},
                    "intervalle": {"joueurs_cibles": ["ARD"], "seuil_profondeur": 300}
                }
            },
            {
                "id": 3, "nom": "Renversement sur ARG", "duree_max": 4.0, 
                "conditions": {
                    "position_absolue": {"role": "ARG", "coords": [1200, 400], "seuil": 500},
                    "intervalle": {"joueurs_cibles": ["ARG"], "seuil_profondeur": 300}
                }
            }
        ]
    }
}

# Ces valeurs doivent correspondre exactement aux chaines de caractères du JSON
EVENEMENTS_REUSSITE_TACTIQUE = ["Goal", "Penatly Shot", "2 Minute Exclusion", "Foul"]
EVENEMENTS_BUT = ["Goal"]
EVENEMENTS_A_VERIFIER_POUR_BUT = ["Penatly Shot"]

# ==========================================
# 2. FONCTIONS UTILITAIRES DE CHARGEMENT
# ==========================================

def charger_donnees(chemin):
    with open(chemin, 'r', encoding='utf-8') as f:
        return json.load(f)

def recuperer_joueurs_equipe(donnees, nom_equipe):
    """Récupère les IDs des joueurs appartenant à l'équipe cible."""
    joueurs = donnees['resume']['players']
    return {pid: info for pid, info in joueurs.items() if info['team'] == nom_equipe}

def recuperer_joueurs_sur_terrain(donnees_frame, ids_joueurs_equipe):
    """Filtre les coordonnées pour ne garder que l'équipe concernée."""
    joueurs_actifs = []
    for pid, coords in donnees_frame.items():
        if pid in ids_joueurs_equipe:
            joueurs_actifs.append({'id': pid, 'x': coords['x'], 'y': coords['y']})
    return joueurs_actifs

def identifier_et_retirer_gardien(joueurs, x_but):
    """Le joueur le plus proche de son propre but est considéré comme gardien."""
    if not joueurs: return None, []
    # Tri par distance au but
    joueurs_tries = sorted(joueurs, key=lambda p: np.sqrt((p['x'] - x_but)**2 + p['y']**2))
    return joueurs_tries[0], joueurs_tries[1:]

# ==========================================
# 3. FONCTIONS DE GÉOMÉTRIE & LOGIQUE
# ==========================================

def est_dans_intervalle(attaquant, defenseurs, seuil_profondeur=200):
    """Vérifie si un attaquant est situé spatialement entre deux défenseurs."""
    if len(defenseurs) < 2: return False
    defenseurs_tries = sorted(defenseurs, key=lambda d: d['y'])
    ax, ay = attaquant['x'], attaquant['y']
    
    for i in range(len(defenseurs_tries) - 1):
        d1 = defenseurs_tries[i]
        d2 = defenseurs_tries[i+1]
        
        # Si l'attaquant est dans le couloir Y entre d1 et d2
        if d1['y'] <= ay <= d2['y']:
            moyenne_def_x = (d1['x'] + d2['x']) / 2
            dist_profondeur = abs(ax - moyenne_def_x)
            if dist_profondeur <= seuil_profondeur:
                return True
    return False

def position_valide(attendue, reelle, seuil):
    """
    attendue : tuple (x, y)
    reelle : dict {'x': ..., 'y': ...}
    """
    ax, ay = attendue
    rx, ry = reelle['x'], reelle['y']
    distance = np.sqrt((ax - rx)**2 + (ay - ry)**2)
    return distance <= seuil

def detecter_sequences(donnees):
    """Découpe le match en séquences d'attaque."""
    try:
        ids_france = recuperer_joueurs_equipe(donnees, EQUIPE_CIBLE).keys()
        ids_adversaire = recuperer_joueurs_equipe(donnees, EQUIPE_ADVERSE).keys()
    except KeyError:
        return []

    sequences = []
    carte_evenements = {}
    
    # Chargement des événements
    if 'events' in donnees:
        for periode, evts in donnees['events'].items():
            carte_evenements[periode] = {float(k): v for k, v in evts.items()}

    periodes = ["first_half", "second_half"]
    EVENEMENTS_TERMINAUX = ["Goal", "Goalkeeper Pick-up", "End of Half", "Ball Out of Play", "Time-out", "Stoppage", "2 Minute Exclusion", "Penatly Shot"]
    EVENEMENTS_REPRISE = ["Goalkeeper Throw", "Throw Off", "Throw In"]

    for periode in periodes:
        if periode not in donnees: continue
        donnees_trajectoire = donnees[periode]
        
        # Récupération et tri des timestamps (exclure métadonnées)
        timestamps_tries = sorted([float(ts) for ts in donnees_trajectoire.keys() if ts not in ["nb_players", "max_ts"]])
        if not timestamps_tries: continue

        ts_debut = str(timestamps_tries[0])
        # Déterminer le sens du jeu au début
        xs_debut_fr = [p['x'] for pid, p in donnees_trajectoire[ts_debut].items() if pid in ids_france]
        moyenne_x = np.mean(xs_debut_fr) if xs_debut_fr else 0
        attaque_positive = moyenne_x < 0 
        
        but_x_attaque = 2000 if attaque_positive else -2000
        but_x_defense = -2000 if attaque_positive else 2000
        
        sequence_active = None
        possession_verrouillee = False
        
        for ts in timestamps_tries:
            str_ts = str(ts)
            frame = donnees_trajectoire[str_ts]
            
            evt_actuel = carte_evenements.get(periode, {}).get(ts)
            type_evt = evt_actuel.get("Event") if evt_actuel else None
            
            if type_evt in EVENEMENTS_REPRISE:
                possession_verrouillee = False

            # Récupération positions
            tous_fr = recuperer_joueurs_sur_terrain(frame, ids_france)
            _, joueurs_champ_fr = identifier_et_retirer_gardien(tous_fr, but_x_defense)
            
            tous_adv = recuperer_joueurs_sur_terrain(frame, ids_adversaire)
            _, joueurs_champ_adv = identifier_et_retirer_gardien(tous_adv, but_x_attaque)

            # Vérifier si l'équipe a passé la médiane
            if attaque_positive:
                attaquants_en_zone = [p for p in joueurs_champ_fr if p['x'] > LIGNE_MEDIANE_X + 200]
            else:
                attaquants_en_zone = [p for p in joueurs_champ_fr if p['x'] < LIGNE_MEDIANE_X - 200]
            
            nb_attaquants = len(attaquants_en_zone)
            
            # GESTION SÉQUENCE EN COURS
            if sequence_active is not None:
                sequence_active["etapes"].append({
                    "ts": ts, 
                    "pos_attaquants": joueurs_champ_fr, 
                    "pos_defenseurs": joueurs_champ_adv
                })
                
                # Fin de séquence explicite (But, Faute, etc)
                if type_evt in EVENEMENTS_TERMINAUX:
                    sequence_active["timestamp_fin"] = ts
                    sequence_active["raison_fin"] = type_evt
                    sequences.append(sequence_active)
                    sequence_active = None
                    
                    if type_evt in ["Goal", "Goalkeeper Pick-up", "End of Half"]:
                        possession_verrouillee = True
                
                # Fin de séquence implicite (Repli ou perte de balle)
                elif nb_attaquants < 3: 
                    if ts - sequence_active["timestamp_debut"] > 2.0:
                        sequence_active["timestamp_fin"] = ts
                        sequence_active["raison_fin"] = "Repli/Perte"
                        sequences.append(sequence_active)
                    sequence_active = None
            
            # DÉMARRAGE NOUVELLE SÉQUENCE
            else:
                if nb_attaquants >= 5 and not possession_verrouillee and type_evt not in EVENEMENTS_TERMINAUX:
                    sequence_active = {
                        "periode": periode,
                        "timestamp_debut": ts,
                        "direction_attaque": "positive" if attaque_positive else "negative",
                        "etapes": [{"ts": ts, "pos_attaquants": joueurs_champ_fr, "pos_defenseurs": joueurs_champ_adv}]
                    }
    return sequences

def identifier_roles_attaque(attaquants, but_x):
    roles = {}
    if not attaquants: return roles
    
    # 1. Identifier le Pivot (le plus proche du but en X)
    pivot = min(attaquants, key=lambda p: abs(p['x'] - but_x))
    roles['PVT'] = pivot['id']
    
    # 2. Identifier les joueurs de champ restants (Base arrière + Ailiers)
    joueurs_champ = [p for p in attaquants if p['id'] != roles.get('PVT')]
    
    # 3. Trier par ordonnée Y 
    joueurs_champ.sort(key=lambda p: p['y'])
    
    nb = len(joueurs_champ)
    
    # Attribution logique selon le nombre de joueurs présents
    if nb == 5: 
        roles['ALD'] = joueurs_champ[0]['id'] # Ailier Droit
        roles['ARD'] = joueurs_champ[1]['id'] # Arrière Droit
        roles['DC']  = joueurs_champ[2]['id'] # Demi-Centre
        roles['ARG'] = joueurs_champ[3]['id'] # Arrière Gauche
        roles['ALG'] = joueurs_champ[4]['id'] # Ailier Gauche
        
    return roles


def analyser_sequence_hybride(sequence, schema):
    etapes_schema = schema['etapes']
    
    try:
        premiere_frame = sequence['etapes'][0]['pos_attaquants']
        but_x = 2000 if sequence['direction_attaque'] == 'positive' else -2000
        carte_roles = identifier_roles_attaque(premiere_frame, but_x)
        
        for role in schema['roles_requis']:
            if role not in carte_roles: return False, 0.0, 0
            
        pid1 = carte_roles[schema['roles_requis'][0]]
        pid2 = carte_roles[schema['roles_requis'][1]]
    except:
        return False, 0.0, 0

    idx_etape_courante = 0
    temps_debut_etape = sequence['etapes'][0]['ts']
    nb_etapes_validees = 0
    
    serie_distances_reelles = []
    
    for frame in sequence['etapes']:
        ts = frame['ts']
        joueurs_dict = {p['id']: p for p in frame['pos_attaquants']}
        
        # 1. Collecte DTW (Distance entre les deux joueurs clés)
        if pid1 in joueurs_dict and pid2 in joueurs_dict:
            d = np.sqrt((joueurs_dict[pid1]['x'] - joueurs_dict[pid2]['x'])**2 + (joueurs_dict[pid1]['y'] - joueurs_dict[pid2]['y'])**2)
            serie_distances_reelles.append(d)

        # 2. Validation Étapes
        if idx_etape_courante < len(etapes_schema):
            etape = etapes_schema[idx_etape_courante]
            
            if ts - temps_debut_etape > etape['duree_max']:
                temps_debut_etape = ts 
                continue 

            conditions_remplies = True
            conds = etape['conditions']
            
            # A. Vérifier Proximité
            if 'proximite' in conds:
                c = conds['proximite']
                if pid1 in joueurs_dict and pid2 in joueurs_dict:
                    dist_actuelle = np.sqrt((joueurs_dict[pid1]['x'] - joueurs_dict[pid2]['x'])**2 + (joueurs_dict[pid1]['y'] - joueurs_dict[pid2]['y'])**2)
                    if dist_actuelle > c['distance_max']: conditions_remplies = False
                else: conditions_remplies = False
            
            # B. Vérifier Intervalle
            if conditions_remplies and 'intervalle' in conds:
                c = conds['intervalle']
                defenseurs = frame['pos_defenseurs']
                intervalle_trouve = False
                for role in c['joueurs_cibles']:
                    if role in carte_roles and carte_roles[role] in joueurs_dict:
                        if est_dans_intervalle(joueurs_dict[carte_roles[role]], defenseurs, c['seuil_profondeur']):
                            intervalle_trouve = True
                            break
                if not intervalle_trouve: conditions_remplies = False

            # C. Vérifier Position Absolue
            if conditions_remplies and 'position_absolue' in conds:
                c = conds['position_absolue']
                role_cible = c['role']
                if role_cible in carte_roles and carte_roles[role_cible] in joueurs_dict:
                    joueur = joueurs_dict[carte_roles[role_cible]]
                    
                    # Adaptation selon le sens du jeu (Miroir)
                    target_x, target_y = c['coords'][0], c['coords'][1]
                    if sequence['direction_attaque'] == 'negative':
                        target_x = -target_x
                        target_y = -target_y
                        
                    if not position_valide((target_x, target_y), joueur, c['seuil']):
                        conditions_remplies = False
                else:
                    conditions_remplies = False

            if conditions_remplies:
                idx_etape_courante += 1
                nb_etapes_validees += 1
                temps_debut_etape = ts

    # 3. Calcul du Score DTW
    score_dtw = 9999.0
    modele_a_utiliser = schema.get('modele_dtw')
    if len(serie_distances_reelles) > 5:
        try:
            score_dtw = dtw(serie_distances_reelles, modele_a_utiliser)
        except: score_dtw = 0

    tactique_detectee = (nb_etapes_validees >= len(etapes_schema))
    pourcentage_reussite = (nb_etapes_validees / len(etapes_schema)) * 100

    return tactique_detectee, score_dtw, pourcentage_reussite

def verifier_resultat_global(timestamp_fin, carte_evenements, type_event_fin):
    if type_event_fin == "Goal": return True
    if type_event_fin in EVENEMENTS_A_VERIFIER_POUR_BUT:
        tous_timestamps = sorted(carte_evenements.keys())
        try:
            idx = tous_timestamps.index(timestamp_fin)
            for i in range(1, 3):
                if idx + i >= len(tous_timestamps): break
                evt = carte_evenements[tous_timestamps[idx + i]].get("Event")
                if evt == "Goal": return True
        except ValueError: pass
    return False

# ==========================================
# 4. EXÉCUTION PRINCIPALE
# ==========================================

if __name__ == "__main__":
    try:
        donnees_json = charger_donnees(CHEMIN_FICHIER)
        sequences = detecter_sequences(donnees_json)
        
        carte_globale_evenements = {}
        if 'events' in donnees_json:
            for periode, evts in donnees_json['events'].items():
                for k, v in evts.items(): carte_globale_evenements[float(k)] = v

        print(f"\nAnalyse de {len(sequences)} séquences d'attaque...")
        
        resultats_bruts = []

        for i, seq in enumerate(sequences):
            ts_debut = seq['timestamp_debut']
            duree = seq.get('timestamp_fin', 0) - ts_debut
            
            # On ignore les séquences trop courtes sauf s'il y a but/penalty
            if duree < 2.5 and seq.get('raison_fin') not in ["Goal", "Penatly Shot"]: continue 

            candidats = []
            for nom_tactique, schema in SCHEMAS_TACTIQUES.items():
                detecte, score_dtw, pct_reussite = analyser_sequence_hybride(seq, schema)
                if detecte:
                    candidats.append({
                        'nom': nom_tactique, 
                        'score_dtw': score_dtw,
                        'pct': pct_reussite
                    })

            if candidats:
                # On garde la tactique avec le score DTW le plus bas (la plus ressemblante)
                meilleure_tactique = min(candidats, key=lambda x: x['score_dtw'])
                evt_fin = seq.get('raison_fin', 'Rien')
                ts_fin = seq.get('timestamp_fin')

                # Si c'est une faute, on regarde si un penalty ou exclusion suit immédiatement
                if evt_fin == "Foul":
                    try:
                        tous_ts = sorted(carte_globale_evenements.keys())
                        if ts_fin in carte_globale_evenements:
                             idx = tous_ts.index(ts_fin)
                             for k in range(1, 4):
                                 if idx + k < len(tous_ts):
                                     prochain_evt = carte_globale_evenements[tous_ts[idx + k]].get('Event', '')
                                     if "Penatly" in prochain_evt: evt_fin = "Penatly Shot"; break
                                     elif "Exclusion" in prochain_evt: evt_fin = "2 Minute Exclusion"; break
                    except ValueError: pass

                succes_tactique = evt_fin in EVENEMENTS_REUSSITE_TACTIQUE
                succes_global_but = (evt_fin == "Goal")
                if succes_tactique and not succes_global_but:
                      succes_global_but = verifier_resultat_global(ts_fin, carte_globale_evenements, evt_fin)

                resultats_bruts.append({
                    'id_sequence': i, 
                    'temps_debut': round(ts_debut, 1),
                    'tactique': meilleure_tactique['nom'],
                    'score_dtw': round(meilleure_tactique['score_dtw'], 1),
                    'evenement_fin': evt_fin,
                    'succes_tactique': succes_tactique,
                    'succes_global': succes_global_but,
                })

        if resultats_bruts:
            df = pd.DataFrame(resultats_bruts)
            MAPPAGE_FAMILLES = {"Yugo_Gauche": "Yugo", "Yugo_Droit":  "Yugo"}
            df['Famille'] = df['tactique'].map(MAPPAGE_FAMILLES).fillna(df['tactique'])

            stats = df.groupby('Famille').agg(
                Nb_Sequences=('id_sequence', 'count'),
                Moyenne_Qualite_DTW=('score_dtw', 'mean'),
                Nb_Positifs=('succes_tactique', 'sum'),
                Nb_Buts_Reels=('succes_global', 'sum'),
            )
            stats['% Eff. Tactique'] = (stats['Nb_Positifs'] / stats['Nb_Sequences'] * 100).round(1)
            stats['% Eff. But'] = (stats['Nb_Buts_Reels'] / stats['Nb_Sequences'] * 100).round(1)

            print("\n" + "="*80)
            print(f" RÉSULTATS FINAUX ({EQUIPE_CIBLE})")
            print("="*80)
            print(stats)
            print("\n--- Détail des séquences détectées ---")
            print(df[['id_sequence', 'temps_debut', 'tactique', 'score_dtw', 'evenement_fin', 'succes_global']])
        else:
            print("Aucune tactique détectée avec ces paramètres.")

    except ImportError:
        print("ERREUR : Veuillez installer tslearn (pip install tslearn)")
    except FileNotFoundError:
        print(f"Erreur: Le fichier {CHEMIN_FICHIER} est introuvable.")
