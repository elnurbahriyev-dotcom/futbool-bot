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

# MyMemory API orqali 100% xavfsiz tarjima funksiyasi
def translate_to_uz(text: str) -> str:
    try:
        # Uzun matnni qismlarga bo'lib tarjima qilamiz, bloklanib qolmasligi uchun
        sentences = text.split(". ")
        translated_sentences = []
        for sentence in sentences[:4]: # Faqat birinchi 4 ta gapni tarjima qilamiz
            if not sentence.strip():
                continue
            url = f"https://translated.net{requests.utils.quote(sentence.strip())}&langpair=en|uz"
            response = requests.get(url, timeout=10).json()
            translated_text = response["responseData"]["translatedText"]
            translated_sentences.append(translated_text)
        return ". ".join(translated_sentences) + "."
    except Exception:
        return text

def get_footballer_details(name: str):
    try:
        # Birinchi o'zbekcha Wikipedia'dan qidirib ko'ramiz
        wikipedia.set_lang("uz")
        search_results = wikipedia.search(f"{name.strip()} futbolchi")
        
        # Agar o'zbekchasidan topilmasa, inglizchasidan qidiramiz
        if not search_results:
            wikipedia.set_lang("en")
            search_results = wikipedia.search(f"{name.strip()} footballer")
            
        if not search_results or len(search_results) == 0:
            return {"text": f"? Afsuski, \'{name}\' haqida ma\'lumot topilmadi.", "image": None}
            
        title = search_results[0]
        
        # Sahifani va rasmini inglizcha Wikipedia orqali aniq yuklaymiz (chunki inglizchasida rasmlar ko'p)
        wikipedia.set_lang("en")
        try:
            page = wikipedia.page(title)
            summary_en = wikipedia.summary(title, sentences=5)
            summary_uz = translate_to_uz(summary_en)
            page_url = page.url
        except Exception:
            # Agar inglizchasida xato bersa, o'zbekchasini o'qiymiz
            wikipedia.set_lang("uz")
            page = wikipedia.page(title)
            summary_uz = wikipedia.summary(title, sentences=5)
            page_url = page.url

        image_url = None
        if page.images:
            valid_images = [img for img in page.images if img.lower().endswith((".png", ".jpg", ".jpeg"))]
            if valid_images:
                image_url = valid_images[0]

        text = (
            f"?? **Futbolchi:** {page.title}\n\n"
            f"???? **Batafsil ma\'lumot (O\'zbek tilida):**\n{summary_uz}\n\n"
            f"?? [Wikipedia sahifasi]({page_url})"
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
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
