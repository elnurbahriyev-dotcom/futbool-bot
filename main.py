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
    return "Bot faol!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def get_footballer_details(name: str):
    try:
        # Wikipedia adashib ketmasligi uchun ism yoniga "footballer" so'zini qo'shib qidiramiz
        search_query = f"{name.strip()} footballer"
        
        wikipedia.set_lang("en")
        # Birinchi bo'lib eng yaqin mos keluvchi maqola sarlavhasini aniqlaymiz
        search_results = wikipedia.search(search_query)
        if not search_results:
            return {"text": f"? Afsuski, \'{name}\' haqida ma\'lumot topilmadi.", "image": None}
            
        title = search_results[0]
        
        # Inglizcha sahifadan rasmini olamiz
        image_url = None
        try:
            en_page = wikipedia.page(title)
            if en_page.images:
                valid_images = [img for img in en_page.images if img.lower().endswith((".png", ".jpg", ".jpeg"))]
                if valid_images:
                    image_url = valid_images[0]
        except Exception:
            pass

        # Matnni o'zbekcha Wikipedia'dan qidiramiz (aniq topilgan sarlavha bo'yicha)
        wikipedia.set_lang("uz")
        try:
            summary = wikipedia.summary(title, sentences=8)
            page_url = wikipedia.page(title).url
        except Exception:
            # Agar o'zbekchasida maqola chiqmasa, inglizcha matnni o'zini oladi
            wikipedia.set_lang("en")
            summary = wikipedia.summary(title, sentences=8)
            page_url = wikipedia.page(title).url

        text = (
            f"?? **Futbolchi:** {title}\n\n"
            f"?? **Batafsil ma\'lumot:**\n{summary}\n\n"
            f"?? [Wikipedia sahifasi]({page_url})"
        )
        return {"text": text, "image": image_url}
        
    except wikipedia.exceptions.DisambiguationError as e:
        return {"text": f"? Bir nechta variant topildi. Iltimos, ismini to'liqroq yozing.", "image": None}
    except Exception as e:
        print(f"Xatolik: {e}")
        return {"text": f"? Afsuski, \'{name}\' haqida ma\'lumot topilmadi.", "image": None}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga istalgan futbolchining ismini yozing, men u haqida rasm va to'liq ma\'lumot chiqarib beraman.")

@dp.message()
async def search_player(message: types.Message):
    waiting_msg = await message.answer("?? Futbolchi qidirilmoqda, kuting...")
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
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
