from telethon import functions, types
from .. import loader, utils
import io
import os
def register(cb):
    cb(AvaMod())
class AvaMod(loader.Module):
    """Установка/удаление аватарок через команды"""
    strings = {'name': 'Ava'}
    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []
    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()
    async def avacmd(self, message):
        'Установить аватарку <reply to image>'
        reply = await message.get_reply_message()
        try:
            reply.media.photo
        except:
            await message.edit("ДАЙ МНЕ БЛЯТЬ ФОТО СУКА ТЫ ЕБАНАЯ")
            return
        await message.edit("Качаем фото")
        photo = await message.client.download_media(message=reply.photo)
        up = await message.client.upload_file(photo)
        await message.edit("Ставим аву")
        await message.client(functions.photos.UploadProfilePhotoRequest(up))
        await message.edit("Ава установлена")
        os.remove(photo)
    async def delavacmd(self, message):
        'Удалить текущую аватарку'
        ava = await message.client.get_profile_photos('me', limit=1)
        if len(ava) > 0:
            await message.edit("Удаляем аватарку...")
            await message.client(functions.photos.DeletePhotosRequest(ava))
            await message.edit("Текущая аватарка удалена")
        else:
            await message.edit("ТЫ ЕБЛАН У ТЯ НЕТ АВАТАРКИ!!! КАКОЙ НАХУЙ УДАЛЯТЬ")
    async def delavascmd(self, message):
        'Удалить все аватарки'
        ava = await message.client.get_profile_photos('me')
        if len(ava) > 0:
            await message.edit("Удаляем аватарки...")
            await message.client(functions.photos.DeletePhotosRequest(await message.client.get_profile_photos('me')))
            await message.edit("Аватарки удалены")
        else:
            await message.edit("ТЫ ЕБЛАН У ТЯ НЕТ АВАТАРКОК!!! КАКОЙ НАХУЙ УДАЛЯТЬ")
        

