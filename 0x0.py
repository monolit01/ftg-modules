from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import logging
from requests import post
from random import choice

logger = logging.getLogger(__name__)

def register(cb):
	cb(ZeroXzerOMod())


@loader.tds
class ZeroXzerOMod(loader.Module):
	"""Uploader"""
	strings = {
		"name": "0x0 Uploader"
	}

	async def client_ready(self, client, db):
		self.client = client
	
	
	@loader.sudo
	async def oxocmd(self, message):
		message.edit("<b>⚞-⚟</b>")
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("<b>⚞reply to media⚟</b>")
			return
		media = reply.media
		if not media:
			await message.edit("<b>⚞reply to media⚟</b>")
			return
		file = await message.client.download_file(media)
		try:
			OxO = post('https://0x0.st', files={'file': file})
		except ConnectionError:
			await message.edit("<b>C</b>onne<b>c</b>tionError")
			return
		if str(OxO) != "<Response [200]>":
			await message.edit(OxO.text)
			return
		url = OxO.text
		output = f"{choice(list('⚀⚁⚂⚃⚄⚅'))}<code>{url}</code>"
		await message.edit(output)
	