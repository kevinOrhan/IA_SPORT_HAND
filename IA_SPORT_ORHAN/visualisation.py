import json
import matplotlib.pyplot as plt #type: ignore
import matplotlib.patches as patches
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
FILE_PATH = "data_handball/15_01_16_France_Mens_Handball_v_CzechRepublic_Mens_Handball.json"
TARGET_TEAM = "France"
OPPONENT_TEAM = "CzechRepublic"  # Nom de l'équipe adverse dans le JSON

SEQUENCES_A_COMPARER = [
    {
        "titre": "Seq 5 : YUGO GAUCHE",
        "timestamp": 414,  
        "half": "first_half", 
        "duree": 6
    },
    {
        "titre": "Seq 7 : YAGO",
        "timestamp": 639, 
        "half": "first_half",
        "duree": 4
    },
    {
        "titre": "Seq 10 : ENTREE ALG 2 PIVOTS",
        "timestamp": 881.3, 
        "half": "first_half",
        "duree": 5.5
    },
    {
        "titre": "Seq 15 : ESPAGNOLE AILIER",
        "timestamp": 1234.5, 
        "half": "first_half",
        "duree": 5
    }
]

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_team_players(data, team_name):
    players = data['resume']['players']
    return {pid: info for pid, info in players.items() if info['team'] == team_name}

def dessiner_terrain(ax):
    """Dessine un demi-terrain de handball simplifié"""
    # Lignes de touche et de fond
    ax.plot([-2000, 2000], [-1000, -1000], 'k-', linewidth=2)
    ax.plot([-2000, 2000], [1000, 1000], 'k-', linewidth=2)
    ax.plot([-2000, -2000], [-1000, 1000], 'k-', linewidth=2) # Fond gauche
    ax.plot([2000, 2000], [-1000, 1000], 'k-', linewidth=2)   # Fond droit
    ax.plot([0, 0], [-1000, 1000], 'k--', linewidth=1)        # Ligne médiane

    # Zones (cercles des 6m et 9m approx)
    ax.add_patch(plt.Circle((-2000, 0), 600, color='blue', alpha=0.1))
    ax.add_patch(plt.Circle((-2000, 0), 900, color='blue', fill=False, linestyle=':'))
    
    ax.add_patch(plt.Circle((2000, 0), 600, color='blue', alpha=0.1))
    ax.add_patch(plt.Circle((2000, 0), 900, color='blue', fill=False, linestyle=':'))

def plot_sequence(ax, data, start_ts, duration, team_ids, opp_ids, titre):
    dessiner_terrain(ax)
    
    # Récupération des frames
    timestamps = sorted([float(ts) for ts in data.keys() if ts not in ["nb_players", "max_ts"]])
    try:
        start_idx = min(range(len(timestamps)), key=lambda i: abs(timestamps[i] - start_ts))
    except ValueError:
        return 

    frames_to_plot = []
    for i in range(start_idx, len(timestamps)):
        ts = timestamps[i]
        if ts - start_ts > duration: break
        frames_to_plot.append((ts, data[str(ts)]))

    x_positions_att = [] # Pour le zoom caméra
    
    # --- 1. TRACÉ DES DÉFENSEURS (ADVERSAIRES) ---
    for pid, info in opp_ids.items():
        xs, ys = [], []
        for ts, frame in frames_to_plot:
            if pid in frame:
                xs.append(frame[pid]['x'])
                ys.append(frame[pid]['y'])
        
        if xs:
            mean_x = np.mean(xs)
            if abs(mean_x) < 2500: # Filtre zone de jeu
                # Ligne noire solide
                ax.plot(xs, ys, linewidth=1.5, alpha=0.6, color='black')
                # Petit point noir au début
                ax.scatter(xs[0], ys[0], marker='x', color='black', s=20)

    # --- 2. TRACÉ DES ATTAQUANTS (FRANCE) ---
    colors = plt.cm.tab10(np.linspace(0, 1, 7))
    player_idx = 0

    for pid, info in team_ids.items():
        xs, ys = [], []
        for ts, frame in frames_to_plot:
            if pid in frame:
                xs.append(frame[pid]['x'])
                ys.append(frame[pid]['y'])
        
        if xs:
            mean_x = np.mean(xs)
            if abs(mean_x) < 2500: 
                x_positions_att.append(mean_x)
                c = colors[player_idx % 7]
                
                # Trajectoire colorée
                ax.plot(xs, ys, label=f"{info['name']}", linewidth=2.5, alpha=0.9, color=c)
                # Rond de départ
                ax.scatter(xs[0], ys[0], marker='o', color=c, s=40, zorder=3)
                # Flèche de fin
                if len(xs) > 1:
                    ax.arrow(xs[-2], ys[-2], xs[-1]-xs[-2], ys[-1]-ys[-2], 
                             head_width=40, head_length=40, fc=c, ec=c, zorder=3)
                player_idx += 1

    # --- 3. TRACÉ DE LA BALLE ---
    ball_xs, ball_ys = [], []
    for ts, frame in frames_to_plot:
        if 'ball' in frame:
            ball_xs.append(frame['ball']['x'])
            ball_ys.append(frame['ball']['y'])
    
    if ball_xs:
        # Ligne pointillée gris foncé/orange
        ax.plot(ball_xs, ball_ys, linestyle=':', linewidth=2, color='#444444', label='Balle')


    # --- MISE EN PAGE ---
    if x_positions_att:
        center_gravity = np.mean(x_positions_att)
        if center_gravity > 0:
            ax.set_xlim(0, 2200) # Côté Droit
        else:
            ax.set_xlim(-2200, 0) # Côté Gauche
            
    ax.set_title(titre, loc='left', fontsize=10, fontweight='bold')
    
    # AXE Y INVERSÉ : On passe de (1200, -1200) au lieu de (-1200, 1200)
    ax.set_ylim(1200, -1200) 
    
    # CORRECTION RATIO D'ASPECT
    ax.set_aspect('equal')

    ax.legend(fontsize='xx-small', loc='lower right', ncol=2)
    ax.grid(True, alpha=0.2)

if __name__ == "__main__":
    print("Chargement des données...")
    data_json = load_data(FILE_PATH)
    fr_players = get_team_players(data_json, TARGET_TEAM)
    opp_players = get_team_players(data_json, OPPONENT_TEAM) # Chargement adversaires
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    axes_flat = axes.flatten() 
    
    for i, seq in enumerate(SEQUENCES_A_COMPARER):
        if i >= len(axes_flat): break
        
        print(f"Graphique : {seq['titre']}")
        half_data = data_json[seq['half']]
        
        plot_sequence(axes_flat[i], half_data, seq['timestamp'], seq['duree'], 
                      fr_players, opp_players, seq['titre'])

    plt.tight_layout()
    plt.show()
    print("Terminé.")