import discord
from discord.ext import commands
from gtts import gTTS as gtts

class TTS(commands.Cog):
    """Text to Speech"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name = 'tts', aliases = ['texttospeech', 'tss', 'ts', 'ttts'])
    async def _tts(self, ctx, userText : str, *args):
        """Odtwarza dźwięk wpisany przez użytkownika (yo tts [tekst])"""
        #get text after space
        spaceText = ""
        for txt in args:
            spaceText += (" " + str(txt))

        txt = (userText + spaceText) #combine text

        #generate tts
        if(len(txt) > 0 and txt != ' '):
            message = gtts(txt, lang = self.bot.data["ttsLang"], tld=self.bot.data["ttsTld"])
            message.save(self.bot.data['ttsAudioPath'] + 'tts.mp3')

            vc = await self.Join(ctx) #join vc

            await self.PlaySound(ctx, vc) #play tts

            await ctx.reply("Odtwarzam TTS: `" + txt + "`", delete_after=5)

    
    async def Join(self, ctx):
        user=ctx.message.author #get user
        voice_channel=user.voice.channel #get user's vc

        same_channel = False

        if voice_channel != None: #user has to be in the vc
            if(self.bot.voice_clients != []): #if bot is on any server's vc
                for server in self.bot.voice_clients: #cycle through all servers
                    if(server.channel == voice_channel): #bot is already on the same vc
                        same_channel = True
                        break

                if same_channel == False: #User is on the same server's vc, but not the same channel
                    return await voice_channel.connect()
                    await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)

            else:
                return await voice_channel.connect() #connect to the requested channel, bot isn't connected to any of the server's vc
                await ctx.reply("Dołączam na kanał `" + str(voice_channel.name) + "`", delete_after=5)


    def PlaySound(self, channel : discord.VoiceChannel):
        for server in self.bot.voice_clients: #cycle through all servers
            if(server.channel == channel): #find current voice channel
                vc = server #get voice channel

                if vc.is_playing() == False: #if not saying something
                        vc.play(discord.FFmpegPCMAudio(self.bot.data['ttsAudioPath'] + 'tts.mp3'), after=lambda e: print('Player error: %s' % e) if e else None) #play sound on vc

                break 

def setup(bot):
    bot.add_cog(TTS(bot))