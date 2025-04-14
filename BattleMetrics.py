import requests
import re

#########################################################################################

def extract_server_id(url):
    match = re.search(r'(\d+)$', url)
    return match.group(1) if match else None

#########################################################################################

def get_server_data(server_id):
    url = f"https://api.battlemetrics.com/servers/{server_id}?include=player"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[!] Error fetching data: {e}")
        return None

#########################################################################################

def extract_player_info(players):
    player_list = []
    for player in players:
        name = player.get("attributes", {}).get("name", "Unknown")
        player_id = player.get("id", "N/A")
        player_list.append((name, player_id))
    return player_list

#########################################################################################