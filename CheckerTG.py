from .. import loader, utils
import requests
def register(cb):
	cb(CheckerTGMod())
class CheckerTGMod(loader.Module):
	"""CheckerTG"""
	strings = {
		'name': 'CheckerTG',
		'check': '[DEK_API] Делаем запрос к API...'
		}
	def __init__(self):
		self.name = self.strings['name']
		self._me = None
		self._ratelimit = []
	async def client_ready(self, client, db):
		self._db = db
		self._client = client
		self.me = await client.get_me()
	async def checkcmd(self, m):
		""" Проверить uid на номер
		Отправляет данные в чат
		Жуёт либо <reply> либо <uid>
		"""
		reply = await m.get_reply_message()
		if utils.get_args_raw(m):
			user = utils.get_args_raw(m)
		elif reply:
			try:
				user = str(reply.sender.id)
			except:
				await m.edit("<b>Err</b>")
				return
		else:
			await m.edit("[DEK_API] А кого чекать?")
			return
		await m.edit(self.strings['check'])
		await m.edit(f"[DEK_API] Ответ API: <code>{requests.get('http://d4n13l3k00.ml/api/checkTgId?uid=' + user).json()['data']}</code>")
	async def scheckcmd(self, m):
		""" Проверить uid на номер
		Отправляет данные в избранное
		Жуёт либо <reply> либо <uid>
		"""
		reply = await m.get_reply_message()
		if utils.get_args_raw(m):
			user = utils.get_args_raw(m)
		elif reply:
			try:
				user = str(reply.sender.id)
			except:
				await m.edit("<b>Err</b>")
				return
		else:
			await m.edit("А кого пробивать?")
			return
		await m.edit(self.strings['check'])
		await m.client.send_message("me", f"[DEK_API] Ответ API: <code>{requests.get('http://d4n13l3k00.ml/api/checkTgId?uid=' + user).json()['data']}</code>")
		await m.edit(f"[DEK_API] Ответ API отправлен в избранное!")
		