from dataclasses import dataclass
from classes.VideoObject import VideoObject

@dataclass
class PlaylistVideo(VideoObject):
	index: int

	@classmethod
	def create(cls, videoObject: VideoObject, index: int):
		return cls(
			videoObject.title,
			videoObject.author,
			videoObject.videoId,
			videoObject.authorId,
			index
		)