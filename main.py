import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

# --- CONFIGURATION ---
API_TOKEN = "iOmq7nkJkkx72Eyit81eRETKe5x-EehrrznAcTXaVvCaVSv2CdM"
TEAM_ID = "3455" 
# On filtre pour n'avoir que les matchs futurs de 2026
URL = f"https://api.pandascore.co/teams/3455/matches?token=iOmq7nkJkkx72Eyit81eRETKe5x-EehrrznAcTXaVvCaVSv2CdM&filter[future]=true&sort=begin_at"

def generate_vitality_calendar():
    response = requests.get(URL)
    if response.status_code != 200:
        print("Erreur API")
        return
    
    matches = response.json()
    
    cal = Calendar()
    cal.add('prodid', '-//Vitality CS Calendar//FR')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Vitality CS 2026') 

    for match in matches:
        if not match.get('begin_at') or match.get('status') == 'canceled':
            continue

        event = Event()
        
        # --- LOGIQUE POUR TROUVER L'ADVERSAIRE ---
        opponent_name = "Adversaire à déterminer"
        if match.get('opponents'):
            for opp in match['opponents']:
                # On compare l'ID pour ne pas s'afficher soi-même
                if str(opp['opponent']['id']) != TEAM_ID:
                    opponent_name = opp['opponent']['name']
                    break
        
        # --- NOM DE L'ÉVÉNEMENT (TOURNOI) ---
        tournament = match['league']['name']
        # Titre du calendrier : Vitality vs Adversaire (Nom du Tournoi)
        match_summary = f"Vitality vs {opponent_name} [{tournament}]"
        
        # --- GESTION DES DATES ---
        start_time = datetime.strptime(match['begin_at'], '%Y-%m-%dT%H:%M:%SZ')
        start_time = start_time.replace(tzinfo=pytz.UTC)
        # Fin du match estimée à +3h
        end_time = start_time + timedelta(hours=3)
        
        # --- CONSTRUCTION ---
        event.add('summary', match_summary)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('description', f"Tournoi : {tournament}\nType : {match['match_type'].upper()}\nStream : {match.get('official_stream_url', 'Non défini')}")
        event.add('uid', str(match['id']) + "@vitality.fans")
        
        cal.add_component(event)

    with open("vitality_matches.ics", "wb") as f:
        f.write(cal.to_ical())
    print("Fichier mis à jour avec les adversaires et tournois !")

generate_vitality_calendar()
