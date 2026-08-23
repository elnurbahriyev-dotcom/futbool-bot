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

# Google Translate orqali matnni o'zbekchaga o'girish funksiyasi
def translate_to_uz(text: str) -> str:
    try:
        url = f"https://googleapis.com{requests.utils.quote(text)}"
        response = requests.get(url, timeout=10).json()
        translated_text = "".join([sentence[0] for sentence in response[0] if sentence[0]])
        return translated_text
    except Exception:
        return text # Xato bo'lsa inglizcha matn qaytadi

def get_footballer_details(name: str):
    try:
        # 1. Aniq topish uchun inglizcha qidiruvni ishlatamiz (Eldor Shomurodov aniq chiqadi)
        wikipedia.set_lang("en")
        search_query = f"{name.strip()} footballer"
        search_results = wikipedia.search(search_query)
        
        if not search_results:
            return {"text": f"? Afsuski, \'{name}\' haqida ma\'lumot topilmadi.", "image": None}
            
        title = search_results
        page = wikipedia.page(title)
        
        # 2. Inglizcha to'liq matnni ajratib olamiz
        summary_en = wikipedia.summary(title, sentences=6)
        
        # 3. Matnni avtomatik O'zbekchaga tarjima qilamiz
        summary_uz = translate_to_uz(summary_en)
        
        # 4. Rasmini ajratib olamiz
        image_url = None
        if page.images:
            valid_images = [img for img in page.images if img.lower().endswith((".png", ".jpg", ".jpeg"))]
            if valid_images:
                image_url = valid_images

        text = (
            f"?? **Futbolchi:** {page.title}\n\n"
            f"???? **Batafsil ma\'lumot (O\'zbek tilida):**\n{summary_uz}\n\n"
            f"?? [Wikipedia sahifasi]({page.url})"
        )
        return {"text": text, "image": image_url}
        
    except Exception as e:
        print(f"Xatolik: {e}")
        return {"text": f"? Afsuski, \'{name}\' haqida ma\'lumot topib bo\'lmadi. Ismini to\'g\'ri yozing.", "image": None}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga istalgan futbolchining ismini yozing, men u haqida rasm va o\'zbekcha ma\'lumot chiqarib beraman.")

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
