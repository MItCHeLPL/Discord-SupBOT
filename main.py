import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv() #load .env

#load settings
with open('settings.json') as file:
    bot.data = json.load(file)

bot = commands.Bot(command_prefix='yo ', intents=discord.Intents().all(), case_insensitive=True) #set up bot

#bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('\nConnected to:')
    for guild in bot.guilds:
        print(guild.name)nnnnn

#load modules
for module in bot.data["modules"]:
    bot.load_extension(bot.data["modulePath"] + module)

#start bot
bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)