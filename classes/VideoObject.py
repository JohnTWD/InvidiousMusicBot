from dataclasses import dataclass

@dataclass
class VideoObject:
	title: 	  str
	author:   str
	videoId:  str
	authorId: str

	def returnTupleWithPlaylist(self, playlistId: str) -> tuple[str]:
		return (
			self.title,
			self.author,
			self.videoId,
			self.authorId,
			playlistId
		)