import os
import sqlite3
from classes.PlaylistObject import VideoObject
from classes.PlaylistObject import PlaylistObject

CONST_DBFOLDER: str = os.path.join(os.getcwd(), "databases")

def doesPlaylistExist(playlistID: str, dbConnection: sqlite3.Connection, dbCursor: sqlite3.Cursor) -> bool:
	dbCursor.execute("SELECT 1 FROM playlists WHERE playlistId = ?", (playlistID,))
	return dbCursor.fetchone() is not None

def readPlaylistEntry(
	playlistID: str,
	dbConnection: sqlite3.Connection,
	dbCursor: sqlite3.Cursor,
) -> PlaylistObject:
	dbCursor.execute("SELECT title, author, authorId FROM playlists WHERE playlistId = ?", (playlistID,))
	plMetadata: tuple = dbCursor.fetchone()

	if (plMetadata is None):
		raise ValueError(f"Playlist with ID {playlistID} not found. - Note this should be impossible since there is a check")
	
	dbCursor.execute("SELECT title, author, videoId, authorId FROM videos WHERE playlistId = ?", (playlistID,))
	videoRows: list[tuple[str, str, str, str]] = dbCursor.fetchall()
	videos: list[VideoObject] = []

	for row in videoRows:
		videos.append(VideoObject(row[0], row[1], row[2], row[3]))
	del videoRows

	return PlaylistObject(playlistID, plMetadata[0], plMetadata[1], plMetadata[2], videos)


def modifyPlaylist(
	playlistID: str,
	dbConnection: sqlite3.Connection,
	dbCursor: sqlite3.Cursor,
	shitToRemove: set[VideoObject],
	shitToAdd: set[VideoObject]
) -> None:

	for video in shitToRemove:
		dbCursor.execute("DELETE FROM videos WHERE videoId = ? AND playlistId = ?", (video.videoId, playlistID))

	for video in shitToAdd:
		dbCursor.execute(
			"INSERT OR IGNORE INTO videos (title, author, videoId, authorId, playlistId) VALUES (?, ?, ?, ?, ?)",
			video.returnTupleWithPlaylist(playlistID)
		)

	dbConnection.commit()

def createNewPlaylist(
	playlistID: str,
	dbConnection: sqlite3.Connection, 
	dbCursor: sqlite3.Cursor,
	playlistObject: PlaylistObject
) -> None:
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

def registerPlaylistSchedule(playlistID: str, guildID: int, channelID: int):
	# note channelID is not eternal and this simply stores which channel -ck was last invoked, which can change at any time
	databasePath: str = os.path.join(CONST_DBFOLDER, f"schedule.db")
	dbConnection: sqlite3.Connection = sqlite3.connect(databasePath)
	dbCursor: sqlite3.Cursor = dbConnection.cursor()

	dbCursor.execute("""
		CREATE TABLE IF NOT EXISTS schedule (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			playlistId TEXT,
			guildID INTEGER,
			channelID INTEGER
		)
	""")

	dbCursor.execute(
		"INSERT OR IGNORE INTO schedule (playlistId, guildID, channelID) VALUES (?, ?, ?)",
		(playlistID, guildID, channelID)
	)

	dbConnection.commit()
	dbConnection.close()

def initPlaylistDBEntry(guildId: int) -> tuple[sqlite3.Connection, sqlite3.Cursor]: # WARNING: YOU HAVE TO MANUALLY CLOSE THE CONNECTION LATER
	databasePath: str = os.path.join(CONST_DBFOLDER, f"{guildId}.db")
	dbConnection: sqlite3.Connection = sqlite3.connect(databasePath)
	dbCursor: sqlite3.Cursor = dbConnection.cursor()

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

	return (dbConnection, dbCursor)