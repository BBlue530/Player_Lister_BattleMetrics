import discord
from discord.ext import commands
from Message_Handling import message
from DataBase import set_player_message
from Variables import BOT_TOKEN


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#########################################################################################

@bot.command()
async def helpme(ctx):
    try:
    
        help_commands = "to use this bot use /scan to scan a server and /mark to mark a player"

        await ctx.send(help_commands)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

#########################################################################################

@bot.command()
async def scan(ctx):
    await ctx.send("Enter BattleMetrics server URL:")
    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.TextChannel)
    try:
        user_input = await bot.wait_for('message', check=check, timeout=30.0)
        url = user_input.content.strip()

        server_player_info, marked_players = message(url)

        await ctx.send(server_player_info)
        await ctx.send(marked_players)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

#########################################################################################

@bot.command()
async def mark(ctx):
    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.TextChannel)
    try:
        await ctx.send("Input Player_ID:")
        player_id_input = await bot.wait_for('message', check=check, timeout=30.0)
        player_id = player_id_input.content.strip()
        if not player_id.isdigit():
            await ctx.send("Invalid player ID")
            return

        await ctx.send("Input Message:")
        message_mark_input = await bot.wait_for('message', check=check, timeout=30.0)
        message_mark = message_mark_input.content.strip()

        set_player_message(player_id, message_mark)
        await ctx.send(f"Message for player ID: {player_id} Has been marked: {message_mark}")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

#########################################################################################

bot.run(BOT_TOKEN)