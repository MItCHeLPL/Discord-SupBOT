import discord
from discord.ext import commands
from gtts import gTTS as gtts
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class TTS(commands.Cog):
    """Text to Speech"""
    def __init__(self, bot):
        self.bot = bot

        if self.bot.settings["debug"]["tts"]:
            print(f"[{str(datetime.datetime.utcnow())[0:-7]}][tts]Loaded")
            
    
    async def _tts(self, ctx, txt:str):
        txt = txt.strip().lower() #format text to generate tts

        if(len(txt) > 0):
            message = gtts(txt, lang = self.bot.settings["setting"]["tts"]["ttsLang"], tld=self.bot.settings["setting"]["tts"]["ttsTld"]) #generate tts
            message.save(self.bot.settings['ttsAudioPath'] + 'tts.mp3') #save .mp3

            if self.bot.settings["debug"]["tts"]:
                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][_tts]Generated TTS: {txt}')

            vc = await self.Join(ctx) #join vc

            if vc != None:
                await self.PlaySound(vc) #play tts

                if isinstance(ctx, SlashContext): #slash command
                    await ctx.send("Odtwarzam TTS: `" + txt + "`", hidden=True)
                else: #normal command
                    await ctx.reply("Odtwarzam TTS: `" + txt + "`", delete_after=5)

                if self.bot.settings["debug"]["tts"]:
                    print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][_tts]Playing TTS')

    #normal command
    @commands.command(name = 'tts',
        aliases = ['texttospeech', 'tss', 'ts', 'ttts'], 
        brief = "Wypowiada tekst podany przez użytkownika (yo tts [tekst])", 
        help = "Wypowiada tekst podany przez użytkownika za pomocą syntezatora mowy", 
        usage = "yo tts [tekst]"
    )
    async def _tts_command(self, ctx, text : str, *args):
        if self.bot.settings["debug"]["tts"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][_tts_command]{ctx.author.name} requested normal command')

        #combine text to one string
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))
        text += spaceText

        await self._tts(ctx, text)

    #slash command
    @cog_ext.cog_slash(name="tts", 
        description="Wypowiada tekst podany przez użytkownika", 
        options=[
            create_option(
                name="tekst", 
                description="Podaj tekst do wypowiedzenia", 
                option_type=3, 
                required=True
            )
        ]
    )
    async def _tts_slash(self, ctx:SlashContext, tekst : str):
        if self.bot.settings["debug"]["tts"]:
            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][_tts_slash]{ctx.author.name} requested slash command')

        await self._tts(ctx, tekst)

    
    async def Join(self, ctx):
        user_vc:discord.Member=ctx.author.voice.channel #get user's vc

        same_channel = False

        if user_vc != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for vc in self.bot.voice_clients: #cycle through all servers
                    if(vc.channel == user_vc): #bot is already on the same vc
                        same_channel = True

                        if self.bot.settings["debug"]["tts"]:
                            print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][Join]Bot is in the same vc')

                        return vc #return current channel

                if same_channel == False: #User isn't on the same vc
                    for vc in self.bot.voice_clients: #cycle through all servers
                        if vc.guild == user_vc.guild: #bot is on the same guild, but on other channel

                            if self.bot.settings["debug"]["tts"]:
                                print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][Join]Bot joined vc (bot was on the other channel)')

                            await vc.disconnect() #disconnect from old channel

                            return await user_vc.connect() #join user channel
                    
                    #bot isn't connected to any of the server's vc
                    if self.bot.settings["debug"]["tts"]:
                        print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][Join]Bot joined vc (bot wasnt connected)')

                    return await user_vc.connect() #connect to the requested channel


    async def PlaySound(self, vc : discord.VoiceChannel):
        if vc.is_playing() == True:
            vc.stop() #stop playing

        vc.play(discord.FFmpegPCMAudio(self.bot.settings['ttsAudioPath'] + 'tts.mp3', options = "-loglevel error"), after=lambda e: print('Player error: %s' % e) if e else (print(f'[{str(datetime.datetime.utcnow())[0:-7]}][tts][PlaySound]Played tts on {vc.channel.name}\n') if self.bot.settings["debug"]["tts"] else None)) #play sound on vc


def setup(bot):
    bot.add_cog(TTS(bot))