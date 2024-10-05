import os
import sqlite3
from classes.PlaylistObject import VideoObject
from classes.PlaylistObject import PlaylistObject
from classes.BadPlaylistError import BadPlaylistError
from util.invidious.PlaylistParserUtil import getPlaylist

__dbFolder: str = os.path.join(os.getcwd(), "databases")

async def updatePlaylistAndGetResponse(playlistID: str, guildID: int) -> str:
	databasePath: str = os.path.join(__dbFolder, f"{guildID}.db")
	dbConnection: sqlite3.Connection = sqlite3.connect(databasePath)
	dbCursor: sqlite3.Cursor = dbConnection.cursor()
	playlistObject: PlaylistObject = None

	print("Attempting to get playlist...", end='')
	try:
		playlistObject = await getPlaylist(playlistID)
	except BadPlaylistError as badPlaylistError:
		return repr(badPlaylistError)
	except Exception as genericException:
		return repr(genericException)

	print("Success!")

	dbCursor.execute("""
		CREATE TABLE IF NOT EXISTS playlists (
	    	id INTEGER PRIMARY KEY AUTOINCREMENT,
	    	playlistId TEXT UNIQUE,
	    	title TEXT,
	    	author TEXT,
	    	authorId TEXT
		)"""
	)

	dbCursor.execute("""
		CREATE TABLE IF NOT EXISTS videos (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT,
			author TEXT,
			videoId TEXT,
			authorId TEXT,
			playlistId TEXT,
			FOREIGN KEY (playlistId) REFERENCES playlists (playlistId)
		)"""
	)
	dbConnection.commit()

	dbCursor.execute( # insert playlist metadata info
		"INSERT OR IGNORE INTO playlists (playlistId, title, author, authorId) VALUES (?, ?, ?, ?)",
		playlistObject.returnMetadataTuple()
	)

	for videoObject in playlistObject.videos: # insert all the videos
		assert isinstance(videoObject, VideoObject)

		dbCursor.execute(
			"INSERT OR IGNORE INTO videos (title, author, videoId, authorId, playlistId) VALUES (?, ?, ?, ?, ?)",
			videoObject.returnTupleWithPlaylist(playlistObject.playlistId)
		)

	dbConnection.commit()
	dbConnection.close()

	return f"Sucessful creation of database for playlist {playlistID}"