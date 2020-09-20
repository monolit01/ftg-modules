from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageMediaDocument
from .. import loader, utils


def register(cb):
	cb(dmt228Mod())


class dmt228Mod(loader.Module):
    """Демотиватор 228 @super_rjaka_demotivator_bot"""

    strings = {'name': 'Демотиватор 228'}

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def dmtcmd(self, message):
        """ .dmt [текст по желанию] <reply to video, photo or gif>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to media</b>")
            return
        try:
           media = reply.media
        except:
            await message.edit("<b>Only media</b>")
            return           

        chat = '@super_rjaka_demotivator_bot'
        await message.edit('<b>Демотивируем...</b>')
        async with message.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=1016409811))
                mm = await message.client.send_file(chat, media, caption = args)  
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await message.reply('<b>Разблокируй @super_rjaka_demotivator_bot</b>')
                return
            await message.delete()
            await response.delete()
            await message.client.send_file(message.to_id, response.media, reply_to=await message.get_reply_message())