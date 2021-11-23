import inspect, logging
from telethon.tl.functions.channels import JoinChannelRequest
from .. import loader, utils, main, security
logger = logging.getLogger(__name__)
@loader.tds
class HelpMod(loader.Module):
	"""Provides this help message"""
	strings = {"name": "Help",
			   "bad_module": "<b>Invalid module name specified</b>",
			   "single_mod_header": "<b>Help for</b> <u>{}</u>:",
			   "single_cmd": "\n• <code><u>{}</u></code>\n",
			   "undoc_cmd": "No docs",
			   "all_header": "<b>Available FTG Modules:</b>",
			   "mod_tmpl": "\n• <b>{}</b>",
			   "first_cmd_tmpl": ": <code>{}",
			   "cmd_tmpl": ", {}"}

	@loader.unrestricted
	async def helpcmd(self, message):
		""".help [module]"""
		args = utils.get_args_raw(message)
		if args:
			module = None
			for mod in self.allmodules.modules:
				if mod.strings("name", message).lower() == args.lower():
					module = mod
			if module is None:
				await utils.answer(message, self.strings("bad_module", message))
				return
			# Translate the format specification and the module separately
			try:
				name = module.strings("name", message)
			except KeyError:
				name = getattr(module, "name", "ERROR")
			reply = self.strings("single_mod_header", message).format(utils.escape_html(name))
			if module.__doc__:
				reply += "\n" + "\n".join("  " + t for t in utils.escape_html(inspect.getdoc(module)).split("\n"))
			else:
				logger.warning("Module %s is missing docstring!", module)
			commands = {name: func for name, func in module.commands.items()
						if await self.allmodules.check_security(message, func)}
			for name, fun in commands.items():
				reply += self.strings("single_cmd", message).format(name)
				if fun.__doc__:
					reply += utils.escape_html("\n".join("  " + t for t in inspect.getdoc(fun).split("\n")))
				else:
					reply += self.strings("undoc_cmd", message)
		else:
			reply = self.strings("all_header", message).format(utils.escape_html((self.db.get(main.__name__,
																							  "command_prefix",
																							  False) or ".")[0]))
			for mod in self.allmodules.modules:
				try:
					name = mod.strings("name", message)
				except KeyError:
					name = getattr(mod, "name", "ERROR")
				if name not in [
					"Logger",
					"Raphielgang Configuration Placeholder",
					"Uniborg configuration placeholder",
				]:
					reply += self.strings("mod_tmpl", message).format(name)
					first = True
					try:
						commands = [name for name, func in mod.commands.items()
									if await self.allmodules.check_security(message, func)]
						for cmd in commands:
							if first:
								reply += self.strings("first_cmd_tmpl", message).format(cmd)
								first = False
							else:
								reply += self.strings("cmd_tmpl", message).format(cmd)
						reply += "</code>"
					except:pass		# TODO: FIX THAT SHIT					
		await utils.answer(message, reply)


	async def client_ready(self, client, db):
		self.client = client
		self.is_bot = await client.is_bot()
		self.db = db
	async def hcmd(self, message):
		""".help [module]"""
		args = utils.get_args_raw(message)
		reply=f'mods count:\t{len(self.allmodules.modules)}\n';lister=[]
		pref=self.db.get('friendly-telegram.main', 'command_prefix', ['.'])[0]
		try:
			commands=[list(i.commands.keys()) for i in self.allmodules.modules]
			for cmd in commands:
				temp=' '.join(cmd); first=False if temp in lister else True
				if first:
					lister.append(f'<b> {pref}</b>'.join(cmd))
					first = False
				else: pass
		except: pass
		await message.edit(reply+' || '.join(lister))

