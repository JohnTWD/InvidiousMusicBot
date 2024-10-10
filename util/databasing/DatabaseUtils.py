import os
import sqlite3
from classes.PlaylistObject import VideoObject
from classes.PlaylistObject import PlaylistObject
from classes.BadPlaylistError import BadPlaylistError
from util.invidious.PlaylistParserUtil import getPlaylist

__dbFolder: str = os.path.join(os.getcwd(), "databases")

def __doesPlaylistExist(playlistID: str, dbConnection: sqlite3.Connection, dbCursor: sqlite3.Cursor) -> bool:
	dbCursor.execute("SELECT 1 FROM playlists WHERE playlistId = ?", (playlistID,))
	return dbCursor.fetchone() is not None

def __readPlaylistEntry(
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

	return PlaylistObject(playlistID, plMetadata[0], plMetadata[1], plMetadata[2], videos)


def __modifyPlaylist(
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

def __createNewPlaylist(
	playlistID: str,
	dbConnection: sqlite3.Connection, 
	dbCursor: sqlite3.Cursor,
	playlistObject: PlaylistObject
) -> None:
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

async def updatePlaylistAndGetResponse(playlistID: str, guildID: int) -> str:
	playlistObject: PlaylistObject = None

	print("Attempting to get playlist...", end='')
	try:
		playlistObject = await getPlaylist(playlistID)
	except BadPlaylistError as badPlaylistError:
		return repr(badPlaylistError)
	except Exception as genericException:
		return repr(genericException)

	print("Successful in getting playlist information!")

	databasePath: str = os.path.join(__dbFolder, f"{guildID}.db")
	with sqlite3.connect(databasePath) as dbConnection:
		dbCursor: sqlite3.Cursor = dbConnection.cursor()
	
		if (__doesPlaylistExist(playlistID, dbConnection, dbCursor)):
			currStoredPlaylist: PlaylistObject = __readPlaylistEntry(playlistID, dbConnection, dbCursor)
	
			missingVid: set[VideoObject] = currStoredPlaylist.getDiff(playlistObject)
			newlyAdded: set[VideoObject] = playlistObject.getDiff(currStoredPlaylist)
	
			__modifyPlaylist(playlistID, dbConnection, dbCursor, missingVid, newlyAdded)
	
			retStr: str = "Playlist updated with changes:"
	
			retStr += "\nVideos added:\n"
			for vid in newlyAdded:
				retStr += f"{vid.returnTupleWithPlaylist(playlistID)}\n"
	
			retStr += "\nVideos removed:\n"
			for vid in missingVid:
				retStr += f"{vid.returnTupleWithPlaylist(playlistID)}\n"
	
			return retStr
	
		__createNewPlaylist(playlistID, dbConnection, dbCursor, playlistObject)
		dbConnection.close()
		return f"Sucessful creation of database for playlist {playlistID}"