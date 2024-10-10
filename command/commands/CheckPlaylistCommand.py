import discord
from command.I_Command import I_Command
from classes.PlaylistObject import VideoObject
from classes.PlaylistObject import PlaylistObject
from classes.BadPlaylistError import BadPlaylistError
from util.invidious.PlaylistParserUtil import getPlaylist
from util.databasing.DatabaseUtils import CONST_DBFOLDER, registerPlaylist, initPlaylistDBEntry, doesPlaylistExist, readPlaylistEntry, createNewPlaylist

class CheckPlaylistCommand(I_Command):
	def __init__(self):
		super().__init__(
			"checkplaylist",
			"ck",
			"If playlist ID is known, checks for any changes, else we simply add to our database.",
			"[Invidious playlist ID]"
		)

	async def onInvoke(self, dcMsg: discord.Message, argsArr: list[str]) -> None:
		await dcMsg.channel.send(f"Args passed: {argsArr[1]}...Loading playlist...")

		playlistObject: PlaylistObject = None
		try:
			playlistObject = await getPlaylist(argsArr[1])
		except BadPlaylistError as badPlaylistError:
			await dcMsg.reply(f"Failed due to bad playlist: {repr(badPlaylistError)}")
			return
		except Exception as genericException:
			await dcMsg.reply(f"Generic exception occured: {repr(genericException)}")
			return

		await dcMsg.channel.send("Successful in getting playlist information!")

		registerPlaylist(playlistObject.playlistId, dcMsg.guild.id, dcMsg.channel.id)
		dbPtr: tuple[sqlite3.Connection, sqlite3.Cursor] = initPlaylistDBEntry(dcMsg.guild.id)
		dbConnection: sqlite3.Connection = dbPtr[0]
		dbCursor: sqlite3.Cursor = dbPtr[1]
		del dbPtr

		if (doesPlaylistExist(playlistObject.playlistId, dbConnection, dbCursor)):
			currStoredPlaylist: PlaylistObject = readPlaylistEntry(playlistObject.playlistId, dbConnection, dbCursor)

			missingVid: set[VideoObject] = currStoredPlaylist.getDiff(playlistObject)
			newlyAdded: set[VideoObject] = playlistObject.getDiff(currStoredPlaylist)
			
			if (len(missingVid) == 0 and len(newlyAdded) == 0):
				await dcMsg.reply("No changes found since last update")
			else:
				modifyPlaylist(playlistObject.playlistId, dbConnection, dbCursor, missingVid, newlyAdded)

				retStr: str = "Playlist updated with changes:"

				retStr += "\nVideos added:\n"
				for vid in newlyAdded:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistObject.playlistId)}`\n"

				retStr += "\nVideos removed:\n"
				for vid in missingVid:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistObject.playlistId)}`\n"

				await dcMsg.reply(retStr)
		else:
			createNewPlaylist(playlistObject.playlistId, dbConnection, dbCursor, playlistObject)
			await dcMsg.reply(f"Sucessful creation of database for playlist {playlistObject.playlistId}")
		
		dbConnection.close()
