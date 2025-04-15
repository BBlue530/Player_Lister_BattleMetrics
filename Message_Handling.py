import boto3
from botocore.exceptions import ClientError
from BattleMetrics import extract_player_info, extract_server_id, get_server_data

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BattleMetrics_Player_Lister')

#########################################################################################

def message(url):
    server_id = extract_server_id(url)

    if not server_id:
        return "[!] Invalid server URL."
    
    data = get_server_data(server_id)
    if not data:
        return "[!] Could not fetch server data."

    server_name = data.get("data", {}).get("attributes", {}).get("name", "Unknown Server")
    players = data.get("included", [])
    player_info = extract_player_info(players)
    
    server_info = f"\nServer: {server_name}\n{len(player_info)} players connected:\n"
    server_player_info = "Current Players Online:\n"
    marked_players = "Current Marked Players Online:\n"
    for name, player_id in player_info:
        name = clean_string(name)
        player_id = clean_string(player_id)

        marked_message = get_marked_message(player_id)

        if marked_message:
            server_player_info += f"{name} - Player ID: {player_id} - Message: {marked_message}\n"
            marked_players += f"{name} - Player ID: {player_id} - Message: {marked_message}\n"
        else:
            server_player_info += f"{name} - Player ID: {player_id}\n"
    
    return server_player_info, marked_players, server_info

def clean_string(s):
    return ''.join(e for e in s if e.isprintable()).strip()

#########################################################################################

def get_marked_message(player_id):
    try:
        response = table.get_item(Key={'Player_ID': player_id})
        if 'Item' in response:
            return response['Item'].get('Mark', None)
        else:
            return None
    except ClientError as e:
        print(f"Error player message: {player_id}: {e}")
        return None
    
#########################################################################################

def parse_player_content(player_content, min_len=1500, max_len=1600):
    lines = player_content.splitlines(keepends=True)
    pages = []
    current_chunk = "```\n"

    for line in lines:
        # Check if adding line would go past max_len
        if len(current_chunk) + len(line) + 3 > max_len:
            if len(current_chunk) >= min_len:
                current_chunk += "```"
                pages.append(current_chunk)
                current_chunk = "```\n"

        current_chunk += line

    if current_chunk.strip() != "```":
        current_chunk += "```"
        pages.append(current_chunk)

    return pages

#########################################################################################