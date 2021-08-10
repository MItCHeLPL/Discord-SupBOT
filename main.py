import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
import datetime
from discord_slash import SlashCommand

load_dotenv() #load .env


bot = commands.Bot(command_prefix='yo ', description='''yo [komenda] [atrybut1] [atrybut2]...''', intents=discord.Intents().all(), case_insensitive=True, strip_after_prefix=True, owner_id=os.getenv('DISCORD_BOT_OWNER_ID')) #set up bot
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True) #set up slash commands


#load settings
with open('settings.json') as file:
    bot.settings = json.load(file)

#load data
with open('data.json') as file:
    bot.data = json.load(file)


#start booting process
if __name__ == "__main__":
    print(f'\n\n[{str(datetime.datetime.utcnow())[0:-7]}][main][__main__]--------SETUP STARTED--------\n')


#load modules
for module in bot.settings["modules"]:
    bot.load_extension(bot.settings["modulePath"] + module)


#bot is initialized, start work
@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'yo help')) #set presence

    if bot.settings["debug"]["main"]:
        print(f'\n[{str(datetime.datetime.utcnow())[0:-7]}][main][on_ready]Logged in as {bot.user.name} (ID: {bot.user.id})')
        print(f'Connected to:')
        for guild in bot.guilds:
            print(f"{guild.name}")

    #save connected guilds into data json
    if bot.settings["setting"]["main"]["save_guilds_on_ready"]:
        #clear current connected guilds
        bot.data["connected_guilds"] = []

        #save guilds
        for guild in bot.guilds:
            bot.data["connected_guilds"].append(guild.id)

        #save to json
        with open('data.json', 'w') as outfile:
            json.dump(bot.data, outfile, indent=4)

        if bot.settings["debug"]["main"]:
            print(f'\n[{str(datetime.datetime.utcnow())[0:-7]}][main][on_ready]Saved connected guilds')

    #complete setup
    print(f"\n[{str(datetime.datetime.utcnow())[0:-7]}][main][on_ready]--------SETUP COMPLETE--------\n\n")


#run bot
bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)