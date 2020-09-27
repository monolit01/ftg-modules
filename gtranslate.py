#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# requires: googletrans

import logging
from googletrans import Translator

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(GTranslateMod())


@loader.tds
class GTranslateMod(loader.Module):
    """Google Translator"""
    strings = {"name": "Google Translator",
               "translated": "<b>[ <code>{frlang}</code> -> </b><b><code>{to}</code> ]</b>\n<code>{output}</code>",
               "invalid_text": "Invalid text to translate",
               "split_error": "Python split() error, if there is -> in the text, it must split!"
               }

    def __init__(self):
        self.commands = {"gtranslate": self.gtranslatecmd}
        self.config = loader.ModuleConfig("DEFAULT_LANG", "en", "Language to translate to by default")

    def config_complete(self):
        self.name = self.strings["name"]
        self.tr = Translator()

    async def gtranslatecmd(self, message):
        """.gtranslate [from_lang->][->to_lang] <text>"""
        args = utils.get_args(message)

        if len(args) == 0 or "->" not in args[0]:
            text = " ".join(args)
            args = ["", self.config["DEFAULT_LANG"]]
        else:
            text = " ".join(args[1:])
            args = args[0].split("->")

        if len(text) == 0 and message.is_reply:
            text = (await message.get_reply_message()).message
        if len(text) == 0:
            await message.edit(self.strings["invalid_text"])
            return
        if args[0] == "":
            args[0] = self.tr.detect(text).lang
        if len(args) == 3:
            del args[1]
        if len(args) == 1:
            logging.error(self.strings["split_error"])
            raise RuntimeError()
        if args[1] == "":
            args[1] = self.config["DEFAULT_LANG"]
        args[0] = args[0].lower()
        logger.debug(args)
        translated = self.tr.translate(text, dest=args[1], src=args[0]).text
        ret = self.strings["translated"]
        ret = ret.format(text=utils.escape_html(text), frlang=utils.escape_html(args[0]),
                         to=utils.escape_html(args[1]), output=utils.escape_html(translated))
        await utils.answer(message, ret)
