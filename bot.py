import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Вставь свой токен сюда
TOKEN = '8706813928:AAGe9TtFxOITM1oWFPVgRvDf6E5L1AqJGsY'

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_FILE = 'database.json'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

players = load_data()

# Список всех обменов
EXCHANGES = [
    ('🍋', 20, '🍈', 1), ('🍈', 10, '🍐', 2), ('🍐', 50, '🥑', 10),
    ('🥑', 200, '🥔', 1), ('🥔', 50, '🍊', 2), ('🍊', 100, '🥕', 5),
    ('🥕', 50, '🌽', 1), ('🌽', 20, '🥒', 1), ('🥒', 50, '🧄', 2),
    ('🧄', 20, '🍄', 1), ('🍄', 10, '🥖', 2), ('🥖', 50, '🫔', 2),
    ('🫔', 500, '🧊', 1), ('🧊', 50, '🥚', 1), ('🥚', 10, '🍳', 1),
    ('🍳', 100, '🥘', 1), ('🥘', 100, '🍲', 1), ('🍲', 200, '🍨', 1),
    ('🍨', 1, '🍇', 2), ('🍇', 20, '🍒', 10), ('🍒', 50, '🍎', 5),
    ('🍎', 20, '🍏', 2), ('🍏', 20, '🍅', 1), ('🍅', 5, '🌶️', 10),
    ('🌶️', 100, '🍑', 5), ('🍑', 20, '🍓', 10), ('🍓', 100, '🥥', 20),
    ('🥥', 100, '🫐', 10), ('🫐', 50, '🥝', 5), ('🥝', 50, '🥦', 10),
    ('🥦', 30, '🫑', 2), ('🫑', 10, '🍞', 1), ('🍞', 10, '🥪', 2),
    ('🥪', 1, '🥞', 2), ('🥞', 100, '🎂', 1), ('🎂', 1, '🪡', 5),
    ('🪡', 10, '🧵', 2), ('🧵', 20, '🧶', 1), ('🧶', 10, '🧩', 5),
    ('🧩', 50, '🃏', 10), ('🃏', 50, '🥉', 20), ('🥉', 100, '🥈', 20),
    ('🥈', 100, '🥇', 10), ('🥇', 50, '🎟️', 5), ('🎟️', 50, '🎫', 1),
    ('🎫', 30, '🏆', 5), ('🏆', 50, '🎁', 1), ('🎁', 10, '⭐️', 5),
    ('⭐️', 50, '🔮', 1), ('🔮', 100, '🧸', 1)
]

def check_exchanges(user_id):
    inv = players[user_id]['inventory']
    made_changes = False
    for item_from, count_from, item_to, count_to in EXCHANGES:
        while inv.get(item_from, 0) >= count_from:
            inv[item_from] -= count_from
            inv[item_to] = inv.get(item_to, 0) + count_to
            made_changes = True
    return made_changes

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎲 Бросить кубик")
    kb.button(text="🎒 Инвентарь")
    kb.button(text="🏆 ТОП")
    await message.answer("привет это игоушка по кубикам!", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message(F.text == "🎲 Бросить кубик")
async def roll_dice(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in players:
        players[user_id] = {"username": message.from_user.username or "Игрок", "rolls": 0, "inventory": {}}
    
    players[user_id]['rolls'] += 1
    dice_msg = await message.answer_dice(emoji="🎲")
    value = dice_msg.dice.value
    
    await asyncio.sleep(3) # Ждем анимацию кубика

    if value >= 5:
        # Начисляем 5 лимонов ТОЛЬКО при 5 или 6
        players[user_id]['inventory']['🍋'] = players[user_id]['inventory'].get('🍋', 0) + 5
        # Проверяем обмены
        check_exchanges(user_id)
        save_data(players)
        await message.answer(f"голос ветра начислено 5🍋")
    else:
        save_data(players)
        await message.answer(f"Выпало {value}. Ничего не начислено, попробуй еще раз!")

@dp.message(F.text == "🎒 Инвентарь")
async def show_inventory(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in players or not players[user_id]['inventory']:
        return await message.answer("Твой инвентарь пока пуст!")
    
    text = "🎒 Твой инвентарь:\n"
    items = [f"{k}: {v}" for k, v in players[user_id]['inventory'].items() if v > 0]
    await message.answer(text + "\n".join(items))

@dp.message(F.text == "🏆 ТОП")
async def show_top(message: types.Message):
    sorted_players = sorted(players.items(), key=lambda x: x[1]['rolls'], reverse=True)[:3]
    top_text = "🏆 ТОП ИГРОКОВ:\n"
    for i, (uid, data) in enumerate(sorted_players, 1):
        inv_str = ", ".join([f"{k}:{v}" for k, v in data['inventory'].items() if v > 0][:3]) # покажем первые 3 предмета
        top_text += f"{i}. @{data['username']} | Бросков: {data['rolls']} | Инв: {inv_str or 'пусто'}\n"
    await message.answer(top_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
