from telethon import functions, types
from .. import loader, utils
import io, os
from PIL import Image
def register(cb): cb(AvaMod())
class AvaMod(loader.Module):
    """Установка/удаление аватарок через команды"""
    strings = {'name': 'Ava'}
    def __init__(self): self.name = self.strings['name']
    async def client_ready(self, client, db): pass
    async def avacmd(self, message):
        'Установить аватарку <reply to image>'
        reply = await message.get_reply_message()
        try: reply.media
        except: return await message.edit("ALO нет медиа/>?")
        await message.edit("Качаем фото")
        photo = await message.client.download_media(message=reply.media)
        up = await message.client.upload_file(photo)
        await message.edit("Ставим аву")
        up = await make_square(reply)
        await message.client(
            functions.photos.UploadProfilePhotoRequest(
                await message.client.upload_file(up)
                )
            )
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
async def make_square(msg):
    '''not checking input'''
    image = Image.open(io.BytesIO(await msg.download_media(bytes)))
    width, height = image.size
    # Calculate the upper left and lower right coordinates for the cropped image
    left = (width - min(width, height)) // 2
    upper = (height - min(width, height)) // 2
    right = left + min(width, height)
    lower = upper + min(width, height)
    image = image.crop((left, upper, right, lower))
    output_bytes = io.BytesIO()
    image.save(output_bytes, format='JPEG', quality=100)
    output_bytes.seek(0)
    return output_bytes
