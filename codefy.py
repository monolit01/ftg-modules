import asyncio
from .. import loader, utils
@loader.tds
class CodefyMod(loader.Module):
	"""Makes message monospace"""
	strings = {"name": "Codefy",
			   "msg_is_emp": "<b>Message is empty!</b>"}
	@loader.ratelimit
	async def codecmd(self, message):
		""".code <text or reply>"""
		if message.is_reply:
			reply = await message.get_reply_message()
			code = reply.raw_text
			code = code.replace("<","&lt;").replace(">","&gt;")
			try: await reply.edit(f"<code>{code}</code>")
			except: pass
			await message.delete()
		else:
			code = message.raw_text[5:]
			try:
				await message.edit(f"<code>{code}</code>")
			except:
				await message.edit(self.strings["msg_is_emp"])
	