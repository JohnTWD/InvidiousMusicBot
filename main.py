import discord
import requests
from command.CommandHandler import tryInvokes
from util.invidious.PlaylistParserUtil import getPlaylist
from constants import currentActiveInstance, getToken, CMD_PREFIX
from util.invidious.AudioStreamGetterUtil import getValidAudioStreamUrls, AudioQuality

class IVMBot(discord.Client):
	async def on_ready(self):
		print(f"{self.user} is alive...")

	async def on_message(self, message: discord.Message):
		if (message.author == self.user):
			return

		if (not message.content.startswith(CMD_PREFIX)):
			return
		
		await tryInvokes(message) # part of CommandHandler
		
def main():
	intents = discord.Intents.default()
	intents.message_content = True
	IVMBotClient = IVMBot(intents=intents)
	IVMBotClient.run(getToken())

if (__name__=="__main__"):	main()
