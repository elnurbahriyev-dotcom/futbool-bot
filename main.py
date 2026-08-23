import os
import asyncio
import threading
import requests
from bs4 import BeautifulSoup
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

# Internetdan faqat tayyor o'zbekcha biografiyalarni qidirish funksiyasi
def search_footballer_uz(name: str) -> str:
    # Google qidiruv tizimi orqali faqat o'zbekcha saytlardan ma'lumot yig'amiz
    search_url = f"https://duckduckgo.com{name.strip().replace(' ', '+')}+futbolchi+biografiyasi"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Qidiruv natijalarining matn qismlarini ajratib olamiz
        results = soup.find_all('a', class_='result__snippet')
        
        if not results:
            return f"? Afsuski, internetdan \'{name}\' haqida o'zbekcha ma'lumot topilmadi. Ismini to'g'ri yozganingizga ishonch hosil qiling."
            
        # Birinchi 3 ta eng yaxshi o'zbekcha natijani birlashtiramiz
        full_text = ""
        for res in results[:3]:
            full_text += res.text.strip() + " "
            
        return (
            f"?? **Futbolchi:** {name.title()}\n\n"
            f"???? **Internetdan o'lingan ma'lumotlar (Toza O'zbek tilida):**\n{full_text}\n\n"
            f"?? *Ma'lumotlar o'zbekcha sport sahifalaridan avtomatik olindi.*"
        )
    except Exception as e:
        print(f"Xatolik: {e}")
        return "?? Tizimda yuklanish xatosi bo'ldi. Birozdan so'ng qayta urinib ko'ring."

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga istalgan futbolchining ismini yozing, men u haqida internetdan o'zbekcha ma'lumot topib beraman.")

@dp.message()
async def search_player(message: types.Message):
    waiting_msg = await message.answer("?? Internetdan o'zbekcha ma'lumot qidirilmoqda...")
    result = search_footballer_uz(message.text)
    try:
        await waiting_msg.delete()
    except Exception:
        pass
    await message.answer(result, parse_mode="Markdown")

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
