from instances import currentActiveInstance
from dataclasses import dataclass
from enum import Enum
import requests

class AudioQuality(Enum):
	HIGHEST_POSSIBLE: 	 	int = 0
	AUDIO_QUALITY_HIGH:  	int = 1
	AUDIO_QUALITY_MEDIUM:	int = 2
	AUDIO_QUALITY_LOW:	 	int = 3
	LOWEST_POSSIBLE:		int = 4

@dataclass
class __AudioStream:
	url			: str
	itemType	: str
	audioQuality: AudioQuality

	def printme(self) -> None:
		print(f"{self.itemType}	{self.audioQuality}	{self.url}")

def __fixUrl(url: str) -> str:
	minIndex: int = url.find("://") + 3
	pathIndex: int = url.find('/', minIndex) # notice how we didnt add `+ 1`, since we are including the inherent `/`
	return currentActiveInstance + url[pathIndex:]

def __getQualityStream(allAudioStreams: list[__AudioStream], selectedQuality: AudioQuality) -> __AudioStream: 
	# TODO: optimize this so that we dont need to loop twice
	bestQuality: AudioQuality = None

	for audioStream in allAudioStreams:
		if (audioStream.audioQuality == selectedQuality):
			yield(audioStream)
			continue # skip rest of the checks since this means a specific quality is wanted

		match selectedQuality:
			case AudioQuality.HIGHEST_POSSIBLE:
				if (bestQuality is None or bestQuality.value > audioStream.audioQuality.value):
					bestQuality = audioStream.audioQuality
		
			case AudioQuality.LOWEST_POSSIBLE:
				if (bestQuality is None or bestQuality.value < audioStream.audioQuality.value):
					bestQuality = audioStream.audioQuality

	if (bestQuality is not None):
		for audioStream in allAudioStreams:		# loop through streams again to find the specific value
			if (audioStream.audioQuality == bestQuality):
				yield(audioStream)

def __strToAudQual(rawAudStr: str) -> AudioQuality:
	for qual in AudioQuality:
		if (rawAudStr == qual.name):
			return qual
	return None


def getValidAudioStreamUrls(videoId: str, selectedQuality: AudioQuality = AudioQuality.HIGHEST_POSSIBLE) -> list[str]:
	apiUrl: str = currentActiveInstance + "/api/v1/videos/" + videoId;
	print(apiUrl)

	response: requests.Response = requests.get(apiUrl)
	if (response.status_code != 200):
		raise Exception(f"Can't fetch video streams ({response.status_code}). TODO: autochange the instance if this happens")

	rawPageJsonData: dict = response.json();

	if (len(rawPageJsonData["adaptiveFormats"]) <= 0):
		raise Exception("Error, no adaptive formats found.")

	allAudioStreams: list[__AudioStream] = []
	for stream in rawPageJsonData["adaptiveFormats"]:
		assert isinstance(stream, dict)
		if ("audio/" in stream["type"]):
			streamQual: AudioQuality = __strToAudQual(stream["audioQuality"]) # convert to an `AudioQuality` enum for ease of processing
			if (streamQual is not None):
				# form a `__AudioStream` object
				audioStream = __AudioStream(
					__fixUrl(stream["url"]),
					stream["type"],
					streamQual
				)
				allAudioStreams.append(audioStream)

	for i in  __getQualityStream(allAudioStreams, selectedQuality):
		i.printme()
			