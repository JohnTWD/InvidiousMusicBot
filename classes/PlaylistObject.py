from dataclasses import dataclass
from classes.PlaylistVideo import PlaylistVideo

@dataclass
class PlaylistObject:
	playlistId: str
	title: 		str
	author: 	str
	authorId: 	str
	videos:		set[PlaylistVideo]
