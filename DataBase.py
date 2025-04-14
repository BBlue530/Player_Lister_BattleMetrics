import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BattleMetrics_Player_Lister')

#########################################################################################

def set_player_message(player_id, message):
    try:
        response = table.put_item(
            Item={
                'Player_ID': player_id,
                'Mark': message
            }
        )
        print(f"Message for player ID {player_id} successfully updated: {message}")
    except ClientError as e:
        print(f"Error setting player message: {e}")

#########################################################################################