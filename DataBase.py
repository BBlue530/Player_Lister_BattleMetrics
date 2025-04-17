import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
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
    except ClientError as e:
        print(f"Error setting player message: {e}")

#########################################################################################

def remove_player_message(player_id):
    try:
        response = table.delete_item(
            Key={
                'Player_ID': player_id,
            }
        )
    except ClientError as e:
        print(f"Error setting player message: {e}")

#########################################################################################