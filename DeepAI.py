# DeepAI for FTG by @dekftgmodules

from .. import loader, utils
import requests
import io

def register(cb):
	cb(deepaiMod())

class deepaiMod(loader.Module):
    strings = {'name': 'DeepAI'}
    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []
    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()
    async def dai_set_tokencmd(self, m):
        self._db.set("deepai", "token", str(m.raw_text.split(" ", 1)[1]))
        await m.edit("[DeepAI] Токен установлен")
    async def cnsfwcmd(self, m):
        """ .cnsfw <reply to photo/sticker> - Check on nsfw content by DeepAI"""
        reply = await m.get_reply_message()
        if not reply:
            await m.edit("<b>Reply to media</b>")
            return
        try:
           media = reply.media
        except:
            await m.edit("<b>Only media</b>")
            return
        token = self._db.get("deepai", "token", None)
        if token:
            await m.edit("[DeepAI] Детектим nsfw...")
            photo = io.BytesIO()
            await m.client.download_media(media, photo)
            photo.seek(0)
            r = requests.post(
                "https://api.deepai.org/api/nsfw-detector",
                files={
                    'image': photo.read(),
                },
                headers={'api-key': token}
            )
            try:
                await m.edit("[DeepAI] Тут Nsfw на " + str(round(r.json()["output"]["nsfw_score"]*100, 1)) + "%")
            except:
                await m.edit(f"[DeepAI] {str(r.json())}")
        else:
            await m.edit("[DeepAI] Укажите токен для работы с API\n<code>.dai_set_token TOKEN</code>")

        
