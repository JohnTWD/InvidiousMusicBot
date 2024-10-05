import os
import aiohttp
import requests
from constants import currentActiveInstance
from classes.VideoObject import VideoObject
from classes.PlaylistObject import PlaylistObject
from classes.BadPlaylistError import BadPlaylistError


async def getPlaylist(playlistID: str) -> PlaylistObject:
	apiUrl: str = currentActiveInstance + "/api/v1/playlists/" + playlistID + "?page=";
	isPlaylistEnd: bool = False
	currentPage: int = 1
	currVidIdx: int = -1   # note, `-1` because index of videos in the api data start at 0
	videoList: list[VideoObject] = []
	rtn: PlaylistObject = None

	async with aiohttp.ClientSession() as asyncWebSession:
		while (not isPlaylistEnd): # TODO: Properly implement backup instances
			response: aiohttp.ClientResponse = await asyncWebSession.get(apiUrl + str(currentPage))
			rawPageJsonData: dict = await response.json()

			if (response.status != 200): 	# some error checking
				if ("error" in rawPageJsonData): # check if the "error" key exists
					errorMessage: str = rawPageJsonData["error"]
					if (errorMessage == "Could not extract playlistSidebarRenderer."):
						raise BadPlaylistError(playlistID)
					else:
						raise Exception(f"Getting playlist ({playlistID}) failed due to {errorMessage}")
				else:
					raise Exception(f"Getting playlist ({playlistID}) failed due to unknown error")

			if (len(rawPageJsonData["videos"]) <= 0):
				isPlaylistEnd = True
				rtn = PlaylistObject(
					playlistID,
					rawPageJsonData["title"],
					rawPageJsonData["author"],
					rawPageJsonData["authorId"],
					videoList
				)
				break 

			# parse in page
			for pageVideo in rawPageJsonData["videos"]:
				assert isinstance(pageVideo, dict)
				pageVideoIdx: int = pageVideo["index"]

				if (currVidIdx < pageVideoIdx): # prevent adding of duplicates
					currVidIdx = pageVideoIdx
					videoObject: VideoObject = VideoObject(
						pageVideo["title"],
						pageVideo["author"],
						pageVideo["videoId"],
						pageVideo["authorId"],
					)
					videoList.append(videoObject)

			# @ pagination end
			currentPage += 1
		
	return rtn