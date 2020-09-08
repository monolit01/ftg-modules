from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import logging
from requests import post

logger = logging.getLogger(__name__)

@loader.tds
class x0Mod(loader.Module):
	"""Uploader"""
	strings = {
		"name": "x0 Uploader"
	}

	async def client_ready(self, client, db):
		self.client = client
	
	
	@loader.sudo
	async def x0cmd(self, message):
		await message.edit("<b>Uploading...</b>")
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("<b>Reply to message!</b>")
			return
		media = reply.media
		if not media:
			file = reply.raw_text
		else:
			file = await self.client.download_file(media)
		try:
			x0at = post('https://x0.at', files={'file': file})
		except ConnectionError as e:
			await message.edit(ste(e))
			return
		url = x0at.text
		output = f'<a href="{url}">URL: </a><code>{url}</code>'
		await message.edit(output)
	