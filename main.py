import os
import asyncio
import threading
import requests
import wikipedia
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = "8936004626:AAGTs-BeUg7tLi1a7OH-zRxXmC0Mr2PP8VI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = Flask("")

@app.route("/")
def home():
    return "Bot faol holatda!"

def run_flask():
    # Render uchun 0.0.0.0 host va aniq port majburiy
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def get_footballer_details(name: str):
    try:
        wikipedia.set_lang("en")
        try:
            en_page = wikipedia.page(name)
            title = en_page.title
            image_url = None
            if en_page.images:
                valid_images = [img for img in en_page.images if img.lower().endswith((".png", ".jpg", ".jpeg"))]
                if valid_images:
                    image_url = valid_images[0]
        except Exception:
            title = name
            image_url = None

        wikipedia.set_lang("uz")
        try:
            summary = wikipedia.summary(title, sentences=10)
            page_url = wikipedia.page(title).url
        except Exception:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(title, sentences=8)
            page_url = wikipedia.page(title).url

        text = (
            f"?? **Futbolchi:** {title}\n\n"
            f"?? **Batafsil ma\'lumot:**\n{summary}\n\n"
            f"?? [Wikipedia sahifasi]({page_url})"
        )
        return {"text": text, "image": image_url}
    except Exception as e:
        print(f"Xatolik: {e}")
        return {"text": f"? Afsuski, ma\'lumot topilmadi.", "image": None}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga istalgan futbolchining ismini yozing, rasm va ma\'lumot chiqaraman.")

@dp.message()
async def search_player(message: types.Message):
    waiting_msg = await message.answer("?? Qidirilmoqda...")
    result = get_footballer_details(message.text)
    try:
        await waiting_msg.delete()
    except Exception:
        pass
    if result["image"]:
        try:
            await message.answer_photo(photo=result["image"], caption=result["text"][:1024], parse_mode="Markdown")
        except Exception:
            await message.answer(result["text"], parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await message.answer(result["text"], parse_mode="Markdown", disable_web_page_preview=True)

async def main():
    print("?? Bot muvaffaqiyatli ishga tushdi...")
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
