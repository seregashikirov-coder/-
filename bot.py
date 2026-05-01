import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = '8706813928:AAGe9TtFxOITM1oWFPVgRvDf6E5L1AqJGsY'

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_FILE = 'database.json'

# --- РАБОТА С ДАННЫМИ ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

players = load_data()

# --- ЦЕПОЧКА ОБМЕНА ---
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

def run_exchanges(uid):
    inv = players[uid]['inventory']
    for f_item, f_count, t_item, t_count in EXCHANGES:
        while inv.get(f_item, 0) >= f_count:
            inv[f_item] -= f_count
            inv[t_item] = inv.get(t_item, 0) + t_count

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎲 Бросить кубик")
    kb.button(text="🎒 Инвентарь")
    kb.button(text="🏆 ТОП")
    await message.answer("привет это игоушка по кубикам!", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message(F.text == "🎲 Бросить кубик")
async def press_button(message: types.Message):
    msg = await message.answer_dice(emoji="🎲")
    await handle_dice_logic(message, msg.dice.value, delay=3.5)

@dp.message(F.dice)
async def manual_dice(message: types.Message):
    if message.dice.emoji == "🎲":
        await handle_dice_logic(message, message.dice.value, delay=1.5)

async def handle_dice_logic(message, value, delay):
    uid = str(message.from_user.id)
    if uid not in players:
        players[uid] = {
            "username": message.from_user.username or message.from_user.first_name, 
            "rolls": 0, 
            "inventory": {"🍋": 0}
        }
    
    players[uid]['rolls'] += 1
    await asyncio.sleep(delay)

    # Проверка: только если выпало 5 или 6
    if value >= 5:
        players[uid]['inventory']['🍋'] = players[uid]['inventory'].get('🍋', 0) + 5
        run_exchanges(uid)
        
        # Формируем текст инвентаря
        inv_data = players[uid]['inventory']
        inv_text = ", ".join([f"{k}:{v}" for k, v in inv_data.items() if v > 0])
        
        await message.answer(f"голос ветра начислено 5🍋\n\n🎒 Твой инвентарь: {inv_text}")
    else:
        await message.answer(f"Выпало {value}. Голос ветра молчит (нужно 5 или 6).")
    
    save_data(players)

@dp.message(F.text == "🎒 Инвентарь")
async def show_inv(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in players or not any(v > 0 for v in players[uid]['inventory'].values()):
        return await message.answer("У тебя в инвентаре пока пусто!")
    
    items = [f"{k}: {v}" for k, v in players[uid]['inventory'].items() if v > 0]
    await message.answer("🎒 Твой полный инвентарь:\n\n" + "\n".join(items))

@dp.message(F.text == "🏆 ТОП")
async def show_top(message: types.Message):
    if not players:
        return await message.answer("Игроков пока нет!")
        
    top = sorted(players.values(), key=lambda x: x['rolls'], reverse=True)[:3]
    text = "🏆 ТОП-3 ИГРОКА (по броскам):\n\n"
    for i, p in enumerate(top, 1):
        # Показываем последние 3 добытых предмета
        items = [k for k, v in p['inventory'].items() if v > 0]
        inv_preview = "".join(items[-5:]) 
        text += f"{i}. {p['username']}\n   🎲 Бросков: {p['rolls']}\n   📦 Редкое: {inv_preview or '🍋'}\n\n"
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


