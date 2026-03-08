import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# --- CONFIGURATION ---
API_TOKEN = "iOmq7nkJkkx72Eyit81eRETKe5x-EehrrznAcTXaVvCaVSv2CdM"
TEAM_ID = "3455"  # ID officiel de Vitality sur PandaScore
# On ajoute 'upcoming' pour n'avoir que les matchs futurs ou 'sort=begin_at' pour l'ordre chronologique
URL = f"https://api.pandascore.co/teams/3455/matches?token=iOmq7nkJkkx72Eyit81eRETKe5x-EehrrznAcTXaVvCaVSv2CdM&sort=begin_at"

def generate_vitality_calendar():
    # 1. Récupération du JSON
    response = requests.get(URL)
    if response.status_code != 200:
        print("Erreur API")
        return
    
    matches = response.json()
    
    # 2. Initialisation du Calendrier
    cal = Calendar()
    cal.add('prodid', '-//Vitality CS Calendar//FR')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Vitality CS Matches') # Nom qui apparaîtra sur ton iPhone

    for match in matches:
        # On ignore les matchs sans date précise ou annulés
        if not match.get('begin_at') or match.get('status') == 'canceled':
            continue

        event = Event()
        
        # --- EXTRACTION DES DONNÉES ---
        # Nom de l'adversaire (gestion du cas où l'adversaire n'est pas encore connu)
        opponent = "TBD"
        if match['opponents']:
            opponent = match['opponents'][0]['opponent']['name']
        
        tournament = match['league']['name']
        match_name = f"Vitality vs {opponent} ({match['match_type'].upper()})"
        
        # --- GESTION DES DATES ---
        # PandaScore envoie du format : 2024-05-20T15:00:00Z (UTC)
        start_time = datetime.strptime(match['begin_at'], '%Y-%m-%dT%H:%M:%SZ')
        start_time = start_time.replace(tzinfo=pytz.UTC)
        
        # --- CONSTRUCTION DE L'ÉVÉNEMENT ---
        event.add('summary', match_name)
        event.add('dtstart', start_time)
        # On estime la durée à 3h pour bloquer le créneau
        event.add('dtend', start_time.replace(hour=(start_time.hour + 3) % 24))
        event.add('description', f"Tournoi : {tournament}\nStream : {match.get('official_stream_url', 'Non défini')}")
        event.add('uid', str(match['id']) + "@vitality.fans") # Identifiant unique pour éviter les doublons
        
        cal.add_component(event)

    # 3. Écriture du fichier .ics
    with open("vitality_matches.ics", "wb") as f:
        f.write(cal.to_ical())
    print("Fichier vitality_matches.ics généré avec succès !")

generate_vitality_calendar()
