from dataclasses import dataclass
from classes.VideoObject import VideoObject

@dataclass
class PlaylistObject:
	playlistId: str
	title: 		str
	author: 	str
	authorId: 	str
	videos:		list[VideoObject]

	def returnMetadataTuple(self) -> tuple[str]:
		return (
			self.playlistId,
			self.title,
			self.author,
			self.authorId
		)
