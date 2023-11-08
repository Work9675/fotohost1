import asyncio
from typing import List, Union
import requests
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
BOT_TOKEN = "6523855349:AAEdvRIOdk3YmJH74NdgrKZsb6_G6qRiChE"

bot = Bot(token=BOT_TOKEN)# Place your token here
dp = Dispatcher(bot)


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            if not message.photo:
                raise CancelHandler()
            photo = message.photo[-1]
            photo_path = f'photos/{photo.file_id}.jpg'
            await photo.download(photo_path)
            text = message.caption

            while True:
                response = requests.post(
                    url='https://telegra.ph/upload',
                    files={'file': open(f'photos/{photo.file_id}.jpg', 'rb')}
                )
                try:
                    yy = response.text.split('\\')[2]
                    tt = yy.split('"')[0]

                    photo_url = 'https://telegra.ph/file' + tt
                    
                    if not text:
                        await message.reply(
                            f'Фото загружено: \n{photo_url}',
                            disable_web_page_preview=True,
                        )

                    else:
                        await message.reply(
                            f'Коментарий к Фото: {text} \n\n{photo_url}',
                            disable_web_page_preview=True,
                        )
                        
                    break
                except:
                    pass
            os.remove(photo_path)
            

            raise CancelHandler()


        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_albums(message: types.Message, album: List[types.Message] or types.Message):
    """This handler will receive a complete album of any type."""
    
    tet = album[0].caption
    uu = []
    for obj in album:
        if obj.photo:
            photo = obj.photo[-1]
            file_id = obj.photo[-1].file_id
            photo_path = f'photos/{file_id}.jpg'
            await photo.download(photo_path)
            while True:
                    response = requests.post(
                        url='https://telegra.ph/upload',
                        files={'file': open(f'photos/{file_id}.jpg', 'rb')}
                    )
                    try:
                        yy = response.text.split('\\')[2]
                        tt = yy.split('"')[0]

                        photo_url = 'https://telegra.ph/file' + tt
                        uu.append(f"{photo_url}\n")
                        
                        break
                    except:
                        pass
            os.remove(photo_path)
    b = ''.join(uu)
    if not tet:

        await message.reply(
                        f'Фото Загруженно: \n{b}',
                        disable_web_page_preview=True,
                    )

    else:
        await message.reply(
                        f'Коментарий к Фото: {tet} \n\n{b}',
                        disable_web_page_preview=True,
                    )

   

if __name__ == "__main__":
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True)