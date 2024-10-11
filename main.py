import os
import discord
import requests
from discord.ext import tasks
from command.CommandHandler import tryInvokes
from classes.PlaylistObject import PlaylistObject
from classes.BadPlaylistError import BadPlaylistError
from util.invidious.PlaylistParserUtil import getPlaylist
from constants import currentActiveInstance, getToken, CMD_PREFIX
from util.databasing.DatabaseUtils import initPlaylistDBEntry, readPlaylistSchedule, readPlaylistEntry, createNewPlaylist, modifyPlaylist

def preInit() -> None:
	try:
		os.mkdir("databases")
	except FileExistsError:
		print("Database folder already made, skipping.")

class IVMBot(discord.Client):
	async def on_ready(self):
		print(f"{self.user} is alive...")

	async def on_message(self, message: discord.Message):
		if (message.author == self.user):
			return

		if (not message.content.startswith(CMD_PREFIX)):
			return
			
		await tryInvokes(message) # part of CommandHandler

	async def setup_hook(self) -> None:
		self.autoPlaylistCheckTask.start()

	@tasks.loop(hours=2.5)
	async def autoPlaylistCheckTask(self): # this task handles the automatic checking of playlists
		schedRows: list[tuple[str, int, int]] = readPlaylistSchedule() # playlistID, guildID, channelID
		print(f"auto check started: {schedRows}", flush=True)

		if (len(schedRows) == 0):
			return # return if playlist schedule is empty

		for schedPtr in schedRows:
			playlistID: str  = schedPtr[0]
			guildID: int = schedPtr[1]
			channel: discord.GuildChannel = self.get_channel(schedPtr[2])

			if (channel is None):
				continue

			playlistObject: PlaylistObject = None
			try:
				playlistObject = await getPlaylist(playlistID)
			except BadPlaylistError as badPlaylistError:
				await channel.send(f"Automatic playlist check {playlistID} | Failed due to bad playlist: {repr(badPlaylistError)}")
				continue
			except Exception as genericException:
				await channel.send(f"Automatic playlist check {playlistID} | Generic exception occured: {repr(genericException)}")
				continue

			dbPtr: tuple[sqlite3.Connection, sqlite3.Cursor] = initPlaylistDBEntry(guildID)
			dbConnection: sqlite3.Connection = dbPtr[0]
			dbCursor: sqlite3.Cursor = dbPtr[1]
			del dbPtr

			currStoredPlaylist: PlaylistObject = readPlaylistEntry(playlistObject.playlistId, dbConnection, dbCursor)

			missingVid: set[VideoObject] = currStoredPlaylist.getDiff(playlistObject)
			newlyAdded: set[VideoObject] = playlistObject.getDiff(currStoredPlaylist)
			
			if (len(missingVid) == 0 and len(newlyAdded) == 0):
				continue
			else:
				modifyPlaylist(playlistObject.playlistId, dbConnection, dbCursor, missingVid, newlyAdded)

				retStr: str = "Automatic playlist check | Playlist updated with changes:"

				retStr += "\nVideos added:\n"
				for vid in newlyAdded:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistObject.playlistId)}`\n"

				retStr += "\nVideos removed:\n"
				for vid in missingVid:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistObject.playlistId)}`\n"

				await channel.send(retStr)

			dbConnection.close()

	@autoPlaylistCheckTask.before_loop
	async def before_autoPlaylistCheckTask(self): # so `autoPlaylistCheckTask` will hold until bot is ready
		await self.wait_until_ready()
		
def main():
	intents = discord.Intents.default()
	intents.message_content = True
	IVMBotClient = IVMBot(intents=intents)
	IVMBotClient.run(getToken())
if (__name__=="__main__"):	preInit(); main();
