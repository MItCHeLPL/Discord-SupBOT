import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
import datetime

load_dotenv() #load .env

bot = commands.Bot(command_prefix='yo ', description='''yo [komenda] [atrybut1] [atrybut2]...''', intents=discord.Intents().all(), case_insensitive=True, strip_after_prefix=True, owner_id=os.getenv('DISCORD_BOT_OWNER_ID')) #set up bot

#load settings
with open('settings.json') as file:
    bot.data = json.load(file)

if __name__ == "__main__":
    if bot.data["debug"]["main"]:
        print(f'\n\n[main][__main__]({datetime.datetime.utcnow()})')
        print(f'[main][__main__]--------SETUP STARTED--------\n')

#bot is ready
@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'yo help')) #set presence

    if bot.data["debug"]["main"]:
        print(f'\n[main][on_ready]Logged in as {bot.user.name} (ID: {bot.user.id})')
        print(f'[main][on_ready]Connected to:')
        for guild in bot.guilds:
            print(f"[main][on_ready]{guild.name}")

        print(f"\n[main][on_ready]--------SETUP COMPLETE--------\n\n")

#load modules
for module in bot.data["modules"]:
    bot.load_extension(bot.data["modulePath"] + module)

#start bot
bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)