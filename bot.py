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
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

players = load_data()

# Твоя огромная цепочка обмена
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎲 Бросить кубик")
    kb.button(text="🎒 Инвентарь")
    kb.button(text="🏆 ТОП")
    await message.answer("привет это игоушка по кубикам!", reply_markup=kb.as_markup(resize_keyboard=True))

# РЕАКЦИЯ НА КНОПКУ
@dp.message(F.text == "🎲 Бросить кубик")
async def press_button(message: types.Message):
    # Бот сам кидает кубик (тот самый анимированный стикер)
    msg = await message.answer_dice(emoji="🎲")
    await handle_dice_logic(message, msg.dice.value, delay=3.5)

# РЕАКЦИЯ НА ТВОЙ КУБИК (ЕСЛИ КИНУЛ САМ)
@dp.message(F.dice)
async def manual_dice(message: types.Message):
    if message.dice.emoji == "🎲":
        await handle_dice_logic(message, message.dice.value, delay=1.5)

async def handle_dice_logic(message, value, delay):
    uid = str(message.from_user.id)
    if uid not in players:
        players[uid] = {"username": message.from_user.username or message.from_user.first_name, "rolls": 0, "inventory": {}}
    
    players[uid]['rolls'] += 1
    await asyncio.sleep(delay) # Ждем пока докрутится кубик

    if value >= 5:
        players[uid]['inventory']['🍋'] = players[uid]['inventory'].get('🍋', 0) + 5
        run_exchanges(uid)
        await message.answer(f"голос ветра начислено 5🍋")
    else:
        await message.answer(f"Выпало {value}. Ничего не дали!")
    save_data(players)

@dp.message(F.text == "🎒 Инвентарь")
async def show_inv(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in players or not players[uid]['inventory']:
        return await message.answer("Пусто!")
    items = [f"{k}: {v}" for k, v in players[uid]['inventory'].items() if v > 0]
    await message.answer("🎒 Твой инвентарь:\n" + "\n".join(items))

@dp.message(F.text == "🏆 ТОП")
async def show_top(message: types.Message):
    top = sorted(players.values(), key=lambda x: x['rolls'], reverse=True)[:3]
    text = "🏆 ТОП-3 ИГРОКОВ:\n\n"
    for i, p in enumerate(top, 1):
        inv = "".join([k for k, v in p['inventory'].items() if v > 0][-5:])
        text += f"{i}. {p['username']}\nБросков: {p['rolls']}\nИнв: {inv or '🍋'}\n\n"
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

