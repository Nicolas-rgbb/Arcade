import discord
from discord import app_commands
from discord.ext import commands
import os
import subprocess
import json
import re

# Load .env for Discord token
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')  # Optionally, you can restrict commands to a specific guild

# GitHub URL validator regex (tillader dybere stier)
GITHUB_URL_PATTERN = r'^https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9._-]+(\/[a-zA-Z0-9._-]+)*(\.git)?$'

# Bot intents and setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store GitHub repositories
REPOS_FILE = 'repos.json'

# Initialize repository storage if not exists
if not os.path.exists(REPOS_FILE):
    with open(REPOS_FILE, 'w') as f:
        json.dump([], f)

# Sync commands when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print(f'Error syncing commands: {e}')

# Slash command to add a GitHub repo for monitoring with validation
@bot.tree.command(name="add_repo", description="Add a GitHub repository to monitor")
async def add_repo(interaction: discord.Interaction, repo_url: str):
    if re.match(GITHUB_URL_PATTERN, repo_url):
        with open(REPOS_FILE, 'r+') as f:
            repos = json.load(f)
            if repo_url not in repos:
                repos.append(repo_url)
                f.seek(0)
                json.dump(repos, f, indent=4)
                await interaction.response.send_message(f"Repository '{repo_url}' added!")
            else:
                await interaction.response.send_message(f"Repository '{repo_url}' is already being monitored.")
    else:
        await interaction.response.send_message("Invalid GitHub URL. Please ensure the URL starts with 'https://github.com/' and follows the correct format.")

# Slash command to list all GitHub repositories
@bot.tree.command(name="list_repos", description="List all monitored GitHub repositories")
async def list_repos(interaction: discord.Interaction):
    with open(REPOS_FILE, 'r') as f:
        repos = json.load(f)
        if repos:
            await interaction.response.send_message(f"Monitored repositories: {', '.join(repos)}")
        else:
            await interaction.response.send_message("No repositories are being monitored.")

# Slash command to restart the computer
@bot.tree.command(name="restart", description="Restart the computer")
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("Restarting the computer...")
    # Use subprocess to restart the computer
    subprocess.run(["sudo", "reboot"])

# Slash command to run your update script
@bot.tree.command(name="update_games", description="Run the update games script")
async def update_games(interaction: discord.Interaction):
    try:
        # Run the script and capture output
        output = subprocess.check_output(['/home/specialminds/webgames/update-games.sh'], stderr=subprocess.STDOUT)
        await interaction.response.send_message(f"Update script ran successfully:\n```{output.decode()}```")
    except subprocess.CalledProcessError as e:
        await interaction.response.send_message(f"Script failed with error:\n```{e.output.decode()}```")

# Slash command to remove a GitHub repository
@bot.tree.command(name="remove_repo", description="Remove a GitHub repository from monitoring")
async def remove_repo(interaction: discord.Interaction, repo_url: str):
    with open(REPOS_FILE, 'r+') as f:
        repos = json.load(f)
        if repo_url in repos:
            repos.remove(repo_url)
            f.seek(0)
            f.truncate()  # Clear the file before writing updated data
            json.dump(repos, f, indent=4)
            await interaction.response.send_message(f"Repository '{repo_url}' removed!")
        else:
            await interaction.response.send_message(f"Repository '{repo_url}' not found in monitored list.")

# Start bot
bot.run(TOKEN)

