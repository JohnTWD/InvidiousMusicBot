
class BadPlaylistError(Exception):
	def __init__(self, playlistID: str):
		self.message = f"Inputted playlist ID, {playlistID} is invalid!"
		super().__init__(self.message)