from dataclasses import dataclass

@dataclass(frozen=True)
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

	def __eq__(self, other):
		if isinstance(other, VideoObject):
			return (self.videoId, self.authorId) == (other.videoId, other.authorId)
		return False

	def __hash__(self):
		return hash((self.videoId, self.authorId))