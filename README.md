This is a Discord bot that connects to BattleMetrics to scan and monitor the list of players on any game server.
You can mark players with custom notes, search for players live, and keep track of players as they join or leave the server in real-time.
The bot refreshes the player list automatically when monitoring, so you always see the latest players online.

It also uses AWS DynamoDB to save marked players and their notes.
This means that even if the bot restarts, your marked players and messages will still be there.

!scan	Scan a BattleMetrics server and list all players currently online.

!monitor	Continuously monitor a server, refreshing the player list every 30 seconds.

!mark	Mark a player by their Player_ID with a custom message (saved in database).

!unmark	Remove a marked player by their Player_ID.

!helpme	Display the list of available commands and their descriptions.
