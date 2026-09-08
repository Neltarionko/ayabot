import asyncio
import os
import random
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN")

if not ADMIN_ID:
    raise RuntimeError("Не задан ADMIN_ID")

ADMIN_ID = int(ADMIN_ID)


BASE_DIR = Path(__file__).resolve().parent
GIF_DIR = BASE_DIR / "gifs"

GIF_DIR.mkdir(exist_ok=True)


TRIGGERS = (
    "аыа",
)


bot = Bot(TOKEN)
dp = Dispatcher()


def get_gifs():
    return [
        file
        for file in GIF_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in {".mp4", ".gif"}
    ]


@dp.message(Command("id"))
async def show_id(message: Message):
    if message.from_user:
        await message.reply(
            f"Твой Telegram ID: {message.from_user.id}"
        )


@dp.message(Command("count"))
async def count_gifs(message: Message):
    await message.reply(
        f"Гифок: {len(get_gifs())}"
    )


@dp.message(Command("add"))
async def add_gif(message: Message):
    if not message.from_user:
        return

    if message.from_user.id != ADMIN_ID:
        await message.reply("нет")
        return

    replied = message.reply_to_message

    if not replied:
        await message.reply(
            "Ответь командой /add на гифку"
        )
        return

    # Обычная Telegram GIF / mp4-анимация
    if replied.animation:
        media = replied.animation

    # На случай если файл отправлен как документ
    elif replied.document:
        mime_type = replied.document.mime_type or ""

        if mime_type not in {
            "video/mp4",
            "image/gif",
        }:
            await message.reply("Это не гифка")
            return

        media = replied.document

    else:
        await message.reply("Это не гифка")
        return

    original_name = media.file_name or ""
    suffix = Path(original_name).suffix.lower()

    if suffix not in {".mp4", ".gif"}:
        mime_type = media.mime_type or ""

        if mime_type == "image/gif":
            suffix = ".gif"
        else:
            suffix = ".mp4"

    filename = f"{media.file_unique_id}{suffix}"
    destination = GIF_DIR / filename

    if destination.exists():
        await message.reply("Эта гифка уже есть")
        return

    try:
        await bot.download(
            media.file_id,
            destination=destination,
        )

    except Exception as error:
        print(f"Ошибка загрузки: {error}")
        await message.reply(
            "Не смог скачать гифку"
        )
        return

    await message.reply(
        f"Добавил. Теперь гифок: {len(get_gifs())}"
    )


@dp.message()
async def check_aya(message: Message):
    if not message.text:
        return

    text = message.text.lower()

    if not any(
        trigger in text
        for trigger in TRIGGERS
    ):
        return

    gifs = get_gifs()

    if not gifs:
        print("Папка gifs пустая")
        return

    selected = random.choice(gifs)

    try:
        gif = FSInputFile(selected)

        await message.reply_animation(gif)

    except Exception as error:
        print(
            f"Ошибка отправки {selected}: {error}"
        )


async def main():
    print(
        f"Bot started. GIFs: {len(get_gifs())}"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())