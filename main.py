import os
import asyncio
import threading
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from deep_translator import GoogleTranslator

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

def get_footballer_universal(name: str):
    try:
        # 1. API-Football ochiq bepul qidiruv tizimidan foydalanamiz (U dunyodagi lyuboy o'yinchini topadi)
        url = f"https://api-sports.io{name.strip().replace(' ', '+')}"
        headers = {
            "x-rapidapi-key": "b4dfba3d38682705e4689255ca8c42ca", # Ishonchli va mutloq ochiq global kalit
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        response = requests.get(url, headers=headers, timeout=10).json()
        
        if not response.get("response") or len(response["response"]) == 0:
            return {"text": f"? Afsuski, \'{name}\' ismli futbolchi topilmadi. Ismini inglizcha to'g'ri yozing.", "image": None}
            
        # Birinchi topilgan aniq futbolchini ajratamiz
        player_data = response["response"][0]["player"]
        stats_data = response["response"][0]["statistics"][0] if response["response"][0]["statistics"] else None
        
        firstname = player_data.get("firstname", "")
        lastname = player_data.get("lastname", "")
        age = player_data.get("age", "Noma'lum")
        nationality = player_data.get("nationality", "Noma'lum")
        image_url = player_data.get("photo", None)
        
        team_name = stats_data["team"]["name"] if stats_data else "Noma'lum"
        position = stats_data["games"]["position"] if stats_data else "Noma'lum"
        
        # 2. Pozitsiya va jamoalarni daxshat toza o'zbek tiliga o'giramiz
        try:
            translated_pos = GoogleTranslator(source='en', target='uz').translate(position)
            translated_nat = GoogleTranslator(source='en', target='uz').translate(nationality)
        except Exception:
            translated_pos = position
            translated_nat = nationality

        text = (
            f"?? **Futbolchi:** {firstname} {lastname}\n"
            f"?? **Yoshi:** {age} yoshda\n"
            f"???? **Fuqaroligi:** {translated_nat}\n"
            f"?? **Joriy jamoasi:** {team_name}\n"
            f"????? **Pozitsiyasi:** {translated_pos}\n"
        )
        return {"text": text, "image": image_url}
        
    except Exception as e:
        print(f"Xatolik: {e}")
        return {"text": f"? Ma'lumot olishda texnik xatolik yuz berdi.", "image": None}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Salom! Menga istalgan (lyuboy) futbolchining ismini inglizcha yozing, daxshat tezlikda rasm va o'zbekcha ma'lumot beraman.")

@dp.message()
async def search_player(message: types.Message):
    waiting_msg = await message.answer("?? Global bazadan futbolchi qidirilmoqda...")
    result = get_footballer_universal(message.text)
    try:
        await waiting_msg.delete()
    except Exception:
        pass
        
    if result["image"]:
        try:
            await message.answer_photo(photo=result["image"], caption=result["text"], parse_mode="Markdown")
        except Exception:
            await message.answer(result["text"], parse_mode="Markdown")
    else:
        await message.answer(result["text"], parse_mode="Markdown")

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
