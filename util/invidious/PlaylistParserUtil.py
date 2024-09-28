import os
import requests
from instances import currentActiveInstance
from classes.VideoObject import VideoObject
from classes.PlaylistVideo import PlaylistVideo


def getPlaylist(playlistID: str) -> list[PlaylistVideo]: # TODO : put this in its own file later AND have it return a value
	apiUrl: str = currentActiveInstance + "/api/v1/playlists/" + playlistID + "?page=";
	isPlaylistEnd: bool = False
	currentPage: int = 1
	currVidIdx: int = -1   # note, `-1` because index of videos in the api data start at 0
	videoList: list = []

	while (not isPlaylistEnd): # TODO: todo General-1
		response: requests.Response = requests.get(apiUrl + str(currentPage))

		if (response.status_code != 200):
			raise Exception("Can't fetch playlist. TODO: autochange the instance if this happens")

		rawPageJsonData: dict = response.json();

		if (len(rawPageJsonData["videos"]) <= 0):
			isPlaylistEnd = True
			break 

		# parse in page
		for pageVideo in rawPageJsonData["videos"]:
			assert isinstance(pageVideo, dict)
			pageVideoIdx: int = pageVideo["index"]

			if (currVidIdx < pageVideoIdx): # prevent adding of duplicates
				currVidIdx = pageVideoIdx
				playlistVideo: PlaylistVideo = PlaylistVideo(
					pageVideo["title"],
					pageVideo["author"],
					pageVideo["videoId"],
					pageVideo["authorId"],
					currVidIdx
				)
				videoList.append(playlistVideo)

		# @ pagination end
		currentPage += 1
	
	return videoList