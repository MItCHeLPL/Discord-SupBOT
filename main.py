import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv() #load .env

bot = commands.Bot(command_prefix='yo ', description='''yo [komenda] [atrybut1] [atrybut2]...''', intents=discord.Intents().all(), case_insensitive=True, strip_after_prefix=True, owner_id=os.getenv('DISCORD_BOT_OWNER_ID')) #set up bot

#load settings
with open('settings.json') as file:
    bot.data = json.load(file)

#bot is ready
@bot.event
async def on_ready():
    if bot.data["debug"]["main"]:
        print(f'[main][on_ready]Logged in as {bot.user.name} (ID: {bot.user.id})')
        print('\n[main][on_ready]Connected to:')
        for guild in bot.guilds:
            print(guild.name)
        print("[main][on_ready]Setup complete\n")

#load modules
for module in bot.data["modules"]:
    bot.load_extension(bot.data["modulePath"] + module)

#start bot
bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)