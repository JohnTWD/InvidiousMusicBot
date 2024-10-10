import discord
from command.I_Command import I_Command
from classes.PlaylistObject import VideoObject
from classes.PlaylistObject import PlaylistObject
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
			playlistObject = await getPlaylist(playlistID)
		except BadPlaylistError as badPlaylistError:
			await dcMsg.reply(repr(badPlaylistError))
			return
		except Exception as genericException:
			await dcMsg.reply(repr(genericException))
			return

		await dcMsg.channel.send("Successful in getting playlist information!")

		databasePath: str = os.path.join(CONST_DBFOLDER, f"{dcMsg.guild.id}.db")
		dbConnection: sqlite3.Connection = sqlite3.connect(databasePath)
		dbCursor: sqlite3.Cursor = dbConnection.cursor()

		initPlaylistDBEntry(dbConnection, dbCursor)

		if (doesPlaylistExist(playlistID, dbConnection, dbCursor)):
			currStoredPlaylist: PlaylistObject = readPlaylistEntry(playlistID, dbConnection, dbCursor)

			missingVid: set[VideoObject] = currStoredPlaylist.getDiff(playlistObject)
			newlyAdded: set[VideoObject] = playlistObject.getDiff(currStoredPlaylist)
			
			if (len(missingVid) == 0 and len(newlyAdded) == 0):
				await dcMsg.reply("No changes found since last update")
			else:
				modifyPlaylist(playlistID, dbConnection, dbCursor, missingVid, newlyAdded)

				retStr: str = "Playlist updated with changes:"

				retStr += "\nVideos added:\n"
				for vid in newlyAdded:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistID)}`\n"

				retStr += "\nVideos removed:\n"
				for vid in missingVid:
					retStr += f"`{vid.returnTupleWithPlaylist(playlistID)}`\n"

				await dcMsg.reply(retStr)
		else:
			createNewPlaylist(playlistID, dbConnection, dbCursor, playlistObject)
			await dcMsg.reply(f"Sucessful creation of database for playlist {playlistID}")
		
		dbConnection.close()
