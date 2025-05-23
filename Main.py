import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
from Message_Handling import message, parse_player_content
from DataBase import set_player_message, remove_player_message
from Variables import BOT_TOKEN


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#########################################################################################

# Buttons for the monitor command
# LISTEN! I know doing it like this is very ugly but it works
class PlayerPaginationViewMonitor(View):
    def __init__(self, pages, full_data, stop_callback=None, timeout=300):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.full_data = full_data
        self.current_page = 0
        self.message = None
        self.stop_callback = stop_callback

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Find", style=discord.ButtonStyle.success)
    async def find_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Enter username:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=30.0)
            username = msg.content.strip().lower()

            found_lines = [line for line in self.full_data.splitlines() if username in line.lower()]
            if found_lines:
                result = "```\n" + "\n".join(found_lines) + "\n```"
            else:
                result = f"User: '{username}' not found."

            await self.message.channel.send(result)

        except asyncio.TimeoutError:
            await self.message.channel.send("Request Timeout")
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_monitoring(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Monitoring stop", ephemeral=True)
        if self.stop_callback:
            await self.stop_callback()
        self.stop()

#########################################################################################

# Buttons for the scan command
# LISTEN! I know doing it like this is very ugly but it works
class PlayerPaginationViewScan(View):
    def __init__(self, pages, full_data, stop_callback=None, timeout=300):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.full_data = full_data
        self.current_page = 0
        self.message = None
        self.stop_callback = stop_callback

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Find", style=discord.ButtonStyle.success)
    async def find_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Enter username:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=30.0)
            username = msg.content.strip().lower()

            found_lines = [line for line in self.full_data.splitlines() if username in line.lower()]
            if found_lines:
                result = "```\n" + "\n".join(found_lines) + "\n```"
            else:
                result = f"User: '{username}' not found."

            await self.message.channel.send(result)

        except asyncio.TimeoutError:
            await self.message.channel.send("Request Timeout")

# Option to get pinged if a specific player goes offline

#########################################################################################

@bot.command()
async def helpme(ctx):
    try:
        help_commands = """
        **Bot Commands List:**

        `!scan` — Scan a server and list all players online and marked players online.

        `!monitor` — Monitor a server and update the list all players online and marked players online every 30 seconds. (You can stop it with the 'Stop' button.)

        `!mark` — Mark a player by their Player_ID with a custom message.

        `!unmark` — Remove marked player by their Player_ID.

        `!helpme` — Show this help message.
        """
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

        server_player_info, marked_players, server_info = message(url)
        await ctx.send(f"```{server_info}```")
        player_content = f"\n{server_player_info}"
        pages = parse_player_content(player_content)

        view = PlayerPaginationViewScan(pages, player_content)
        view.message = await ctx.send(pages[0], view=view)

        if marked_players.strip():
            await ctx.send(f"```\n{marked_players}```")

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

@bot.command()
async def unmark(ctx):
    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.TextChannel)
    try:
        await ctx.send("Input Player_ID:")
        player_id_input = await bot.wait_for('message', check=check, timeout=30.0)
        player_id = player_id_input.content.strip()
        if not player_id.isdigit():
            await ctx.send("Invalid player ID")
            return

        remove_player_message(player_id)
        await ctx.send(f"Player ID: {player_id} Has been unmarked")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

#########################################################################################

@bot.command()
async def monitor(ctx):
    
    await ctx.send("Enter BattleMetrics server URL:")

    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.TextChannel)

    try:
        user_input = await bot.wait_for('message', check=check, timeout=30.0)
        url = user_input.content.strip()

        view = None
        player_data = None
        marked_player_data = None
        server_info_player_count = None
        monitoring = True

        async def stop_monitoring():
            nonlocal monitoring
            monitoring = False

        while monitoring:
            server_player_info, marked_players, server_info = message(url)
            player_content = f"\n{server_player_info}"
            pages = parse_player_content(player_content)

            if player_data:
                try:
                    await player_data.delete()
                except:
                    pass
            if marked_player_data:
                try:
                    await marked_player_data.delete()
                except:
                    pass
            if server_info_player_count:
                try:
                    await server_info_player_count.delete()
                except:
                    pass

            server_info_player_count = await ctx.send(f"```{server_info}```")
            view = PlayerPaginationViewMonitor(pages, player_content, stop_callback=stop_monitoring)
            player_data = await ctx.send(pages[0], view=view)
            view.message = player_data

            if marked_players.strip():
                marked_player_data = await ctx.send(f"```\n{marked_players}```")
            else:
                marked_player_data = None

            await asyncio.sleep(300)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


#########################################################################################

bot.run(BOT_TOKEN)