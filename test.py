
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from rembg import remove
from PIL import Image
from io import BytesIO
import nest_asyncio
import asyncio

nest_asyncio.apply()

BOT_TOKEN = '7668834365:AAH26VRUz_hHjKzbwSf51uSGBsMD-z-DaPc'
user_backgrounds = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе заменить фон на изображении.\n\n"
        "1️⃣ Сначала отправь мне изображение, которое будет использоваться как фон.\n"
        "2️⃣ Потом отправь фото с объектом — я вставлю его в фон.\n\n"
        "Можно менять фон, отправив новый фон в любой момент."
    )

async def handle_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = await update.message.photo[-1].get_file()
    byte_stream = BytesIO()
    await photo.download_to_memory(byte_stream)
    byte_stream.seek(0)

    bg_img = Image.open(byte_stream).convert("RGBA")
    user_backgrounds[user_id] = bg_img

    await update.message.reply_text("✅ Фон успешно сохранён! Теперь отправь фото с объектом.")

async def handle_foreground(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_backgrounds:
        await update.message.reply_text("❗ Сначала отправь изображение-фон.")
        return

    fg_photo = await update.message.photo[-1].get_file()
    fg_stream = BytesIO()
    await fg_photo.download_to_memory(fg_stream)
    fg_stream.seek(0)

    fg_img = Image.open(fg_stream).convert("RGBA")
    fg_removed = remove(fg_img).convert("RGBA")

    bg_img = user_backgrounds[user_id]
    bg_resized = bg_img.resize(fg_removed.size)
    composed = Image.alpha_composite(bg_resized, fg_removed)

    output = BytesIO()
    output.name = 'composed.png'
    composed.save(output, format='PNG')
    output.seek(0)

    await update.message.reply_photo(photo=output, caption="✨ Вот изображение с новым фоном!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_backgrounds:
        await handle_foreground(update, context)
    else:
        await handle_background(update, context)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🤖 Бот запущен...")
    await app.initialize()
    await app.start()
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
