# Friendly Telegram (telegram userbot)
# Copyright (C) 2018-2020 The Authors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Module usage:
# .quote <Arguments>
# ╰ .quote 5 [Add 5 messages after quote]
# ╰ .quote file [Send quote as file]
# ╰ .quote 5 file [You can use multiple options]
# API creator: @mishase
# Module creator: @DneZyeK
# Updated module: @rf0x1d

# requires: Pillow

import logging
from .. import loader, utils
import telethon
import requests
import io
import PIL
from telethon.tl.types import (MessageEntityBold, MessageEntityItalic,
                               MessageEntityMention, MessageEntityTextUrl,
                               MessageEntityCode, MessageEntityMentionName,
                               MessageEntityHashtag, MessageEntityCashtag,
                               MessageEntityBotCommand, MessageEntityUrl,
                               MessageEntityStrike, MessageEntityUnderline,
                               MessageEntityPhone, ChannelParticipantsAdmins,
                               ChannelParticipantCreator)

logger = logging.getLogger(__name__)


@loader.tds
class QuotesMod(loader.Module):
    """Quotes"""
    strings = {
        "name": "Quotes",
        "processing": "<b>Processing...</b>",
        "processing_api": "<b>API processing...</b>",
        "no_reply": "<b>No reply</b>",
        "mediaType_photo": "Photo",
        "mediaType_video": "Video",
        "mediaType_videomessage": "Videomessage",
        "mediaType_voice": "Voice",
        "mediaType_audio": "Audio",
        "mediaType_poll": "Poll",
        "mediaType_quiz": "Quiz",
        "mediaType_location": "Geolocation",
        "mediaType_gif": "GIF",
        "mediaType_sticker": "Sticker",
        "mediaType_file": "File: ",
        "diceType_dice": "Dice",
        "diceType_dart": "Dart",
        "ball_thrown": "Ball throw",
        "dart_thrown": "Dart throw",
        "dart_almostthere": "almost there!",
        "dart_missed": "miss!",
        "dart_bullseye": "bullseye!"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def quotecmd(self, message):
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply", message))
            return
        await utils.answer(message, self.strings("processing", message))

        if not args or not args[0].isdigit():
            count = 1
        else:
            count = int(args[0].strip()) + 1
        byfile = False
        if "file" in args:
            byfile = True
        msgs = []
        cur = reply.id
        cyr = cur + count
        while cur != cyr:
            msg = await message.client.get_messages(message.to_id, ids=cur)
            if msg:
                msgs.append(msg)
            cur += 1

        messages = []
        avatars = {}
        for reply in msgs:
            text = reply.raw_text
            entities = parse_entities(reply)
            if reply.fwd_from:
                id = reply.fwd_from.from_id or reply.fwd_from.channel_id
                if not id:
                    id = 1234567890
                    name = reply.fwd_from.from_name
                    pfp = None
                else:
                    sender = await message.client.get_entity(id)
                    name = telethon.utils.get_display_name(sender)
                    pfp = avatars.get(id, None)
                    if not pfp:
                        pfp = await message.client.download_profile_photo(id, bytes)
                        if pfp:
                            pfp = "https://telegra.ph" + requests.post("https://telegra.ph/upload", files={
                                "file": ("file", pfp, None)}).json()[0]["src"]
                            avatars[id] = pfp
            else:
                id = reply.from_id
                sender = await message.client.get_entity(id)
                name = telethon.utils.get_display_name(sender)
                pfp = avatars.get(id, None)
                if not pfp:
                    pfp = await message.client.download_profile_photo(id, bytes)
                    if pfp:
                        pfp = "https://telegra.ph" + requests.post("https://telegra.ph/upload", files={
                            "file": ("file", pfp, None)}).json()[0]["src"]
                        avatars[id] = pfp

            image = await check_media(message, reply)

            rreply = await reply.get_reply_message()
            if rreply:
                rtext = rreply.raw_text
                if rreply.media:
                    rtext = await get_media_caption(rreply)
                rsender = rreply.sender
                rname = telethon.utils.get_display_name(rsender)
                rreply = {"author": rname, "text": rtext}

            admintitle = ""
            if message.chat:
                admins = await message.client.get_participants(message.to_id, filter=ChannelParticipantsAdmins)
                if reply.sender in admins:
                    admin = admins[admins.index(reply.sender)].participant
                    if not admin:
                        admintitle = " "
                    else:
                        admintitle = admin.rank
                    if not admintitle:
                        if type(admin) == ChannelParticipantCreator:
                            admintitle = "owner"
                        else:
                            admintitle = "admin"
            messages.append({
                "text": text,
                "picture": image,
                "reply": rreply,
                "entities": entities,
                "author": {
                    "id": id,
                    "name": name,
                    "adminTitle": admintitle,
                    "picture": pfp
                }
            })

        data = {"messages": messages, "maxWidth": 448}
        await utils.answer(message, self.strings("processing_api", message))
        r = requests.post("https://mishase.me/quote", json=data)
        output = r.content
        out = io.BytesIO()
        if not byfile:
            out.name = "quote.webp"
            im = PIL.Image.open(io.BytesIO(output))
            im.save(out, "WEBP")
        else:
            out.write(output)
            out.name = "quote.png"
        out.seek(0)
        await message.client.send_file(
            message.to_id, out, force_document=byfile,
            reply_to=await message.get_reply_message()
        )
        await message.delete()


async def get_media_caption(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            return QuotesMod.strings["mediaType_photo"]
        dice = False
        try:
            dice = True if reply_message.dice else False
        except AttributeError:
            try:
                dice = True if type(
                    reply_message.media) == telethon.tl.types.MessageMediaDice else False
            except AttributeError:
                pass
        if dice:
            dice_type = ""
            dice_text = reply_message.media.value
            if reply_message.media.emoticon == "🎲":
                dice_type = QuotesMod.strings["diceType_dice"]
                return "{} {}: {}".format(reply_message.media.emoticon,
                                          dice_type,
                                          dice_text)
            elif reply_message.media.emoticon == "🎯":
                if dice_text == 1:
                    dice_text = QuotesMod.strings["dart_missed"]
                elif dice_text == 5:
                    dice_text = QuotesMod.strings["dart_almostthere"]
                elif dice_text == 6:
                    dice_text = QuotesMod.strings["dart_bullseye"]
                else:
                    return "{} {}".format(reply_message.media.emoticon,
                                          QuotesMod.strings["dart_thrown"])
                dice_type = QuotesMod.strings["diceType_dart"]
                return "{} {}: {}".format(reply_message.media.emoticon,
                                          dice_type,
                                          dice_text)
            elif reply_message.media.emoticon == "🏀":
                return "{} {}".format(reply_message.media.emoticon,
                                      QuotesMod.strings["ball_thrown"])
            else:
                return "Unsupported dice type ({}): {}"\
                    .format(reply_message.media.emoticon,
                            reply_message.media.value)
        elif reply_message.poll:
            try:
                if reply_message.media.poll.quiz is True:
                    return QuotesMod.strings["mediaType_quiz"]
            except Exception:
                pass
            return QuotesMod.strings["mediaType_poll"]
        elif reply_message.geo:
            return QuotesMod.strings["mediaType_location"]
        elif reply_message.document:
            if reply_message.gif:
                return QuotesMod.strings["mediaType_gif"]
            elif reply_message.video:
                if reply_message.video.attributes[0].round_message:
                    return QuotesMod.strings["mediaType_videomessage"]
                else:
                    return QuotesMod.strings["mediaType_video"]
            elif reply_message.audio:
                return QuotesMod.strings["mediaType_audio"]
            elif reply_message.voice:
                return QuotesMod.strings["mediaType_voice"]
            elif reply_message.file:
                if reply_message.file.mime_type == "application/x-tgsticker":
                    emoji = ""
                    try:
                        emoji = reply_message.media.document.attributes[0].alt
                    except AttributeError:
                        try:
                            emoji = reply_message.media.document.attributes[1].alt
                        except AttributeError:
                            emoji = ""
                    caption = "{} {}".format(
                        emoji, QuotesMod.strings["mediaType_sticker"]
                    ) if emoji != "" else QuotesMod.strings["mediaType_sticker"]
                    return caption
                else:
                    if reply_message.sticker:
                        emoji = ""
                        try:
                            emoji = reply_message.file.emoji
                            logger.debug(len(emoji))
                        except TypeError:
                            emoji = ""
                        caption = "{} {}".format(
                            emoji, QuotesMod.strings["mediaType_sticker"]
                        ) if emoji != "" else QuotesMod.strings["mediaType_sticker"]
                        return caption
                    else:
                        fn = reply_message.media.document.attributes[-1].file_name
                        return QuotesMod.strings["mediaType_file"] + fn
        else:
            return ""
    else:
        return ""

    return ""


def parse_entities(reply):
    entities = []
    if not reply.entities:
        return []
    for entity in reply.entities:
        entity_type = type(entity)
        start = entity.offset
        end = entity.length
        if entity_type is MessageEntityBold:
            etype = "bold"
        elif entity_type is MessageEntityItalic:
            etype = "italic"
        elif entity_type in [MessageEntityUrl, MessageEntityPhone]:
            etype = "url"
        elif entity_type is MessageEntityCode:
            etype = "monospace"
        elif entity_type is MessageEntityStrike:
            etype = "strikethrough"
        elif entity_type is MessageEntityUnderline:
            etype = "underline"
        elif entity_type in [MessageEntityMention, MessageEntityTextUrl,
                             MessageEntityMentionName, MessageEntityHashtag,
                             MessageEntityCashtag, MessageEntityBotCommand]:
            etype = "bluetext"
        entities.append({"type": etype, "offset": start, "length": end})
    return entities


async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if reply.gif or reply.video or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        img = io.BytesIO()
        img.name = "img.png"
        try:
            PIL.Image.open(io.BytesIO(data)).save(img, "PNG")
            link = "https://telegra.ph" + requests.post("https://telegra.ph/upload", files={
                "file": ("file", img.getvalue(), "image/png")}).json()[0]["src"]
            return link
        except Exception:
            return None
