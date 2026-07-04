import asyncio
import sqlite3
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ================= ВСТАВЬ СВОЙ ТОКЕН =================
TOKEN = "8694624181:AAH1eauxl7vxPIynCQnU0JSg4Ujd7YgedYk"
# ====================================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============================================
#  НАСТРОЙКА БАЗЫ ДАННЫХ
# ============================================

def init_db():
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT DEFAULT 'Без категории',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_lore(user_id, category, title, content):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lore (user_id, category, title, content) VALUES (?, ?, ?, ?)', 
                   (user_id, category, title, content))
    conn.commit()
    conn.close()

def search_lore(user_id, query):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, title, content, created_at FROM lore 
        WHERE user_id = ? AND (category LIKE ? OR title LIKE ? OR content LIKE ?)
        ORDER BY created_at ASC
    ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_lore(user_id):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, title, content, created_at FROM lore WHERE user_id = ? ORDER BY created_at ASC', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_lore_by_title(user_id, title):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, title, content, created_at FROM lore WHERE user_id = ? AND title = ?', (user_id, title))
    result = cursor.fetchone()
    conn.close()
    return result

def get_lore_by_category(user_id, category):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, content, created_at FROM lore 
        WHERE user_id = ? AND category = ? 
        ORDER BY created_at ASC
    ''', (user_id, category))
    results = cursor.fetchall()
    conn.close()
    return results

def get_categories(user_id):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM lore WHERE user_id = ? ORDER BY category ASC', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

def get_titles(user_id):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM lore WHERE user_id = ? ORDER BY title ASC', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

def update_lore(user_id, title, new_content):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE lore SET content = ? WHERE user_id = ? AND title = ?', (new_content, user_id, title))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_lore(user_id, title):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lore WHERE user_id = ? AND title = ?', (user_id, title))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_random_lore(user_id):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, content FROM lore WHERE user_id = ? ORDER BY RANDOM() LIMIT 1', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_statistics(user_id):
    conn = sqlite3.connect('lore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lore WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()[0]
    cursor.execute('SELECT category, COUNT(*) FROM lore WHERE user_id = ? GROUP BY category ORDER BY COUNT(*) DESC', (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return total, categories

# ============================================
#  КОМАНДЫ БОТА
# ============================================

@dp.message(Command("start"))
async def start(message: types.Message):
    msg = await message.answer(
        "🍂 Доброго времени суток\n"
        "Я создан для помощи в построении историй и хранения информации, "
        "запоминаю детали которые чаще всего трудно достать из памяти.\n\n"
        "✐ **Мои команды:**\n"
        "• /новый Категория | Название: Текст — сохранить событие\n"
        "• просто напиши слово — найду все упоминания\n"
        "• /категории — список всех твоих категорий\n"
        "• /названия — список всех названий записей\n"
        "• /категория Название — показать все фрагменты из категории\n"
        "• показать фрагмент Название — показать полный текст\n"
        "• изменить фрагмент Название: Новый текст — переписать сюжет\n"
        "• /удалить Название — удалить фрагмент\n"
        "• /все — показать всю историю\n"
        "• /статистика — сколько записей и по категориям\n"
        "• /вдохновение — случайный фрагмент\n\n"
        "📌 Это сообщение закреплено — всегда можешь подсмотреть команды!\n\n"
        "Жду твоих легенд! ✍️",
        parse_mode="Markdown"
    )
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=msg.message_id)
    except Exception:
        pass

@dp.message(Command("инструкция"))
async def instruction(message: types.Message):
    await message.answer(
        "📖 **Как пользоваться ботом:**\n\n"
        "1️⃣ **Добавить запись:**\n"
        "   /новый Категория | Название: Текст\n"
        "   Например: /новый Локации | Город Чайник: Описание города\n\n"
        "2️⃣ **Найти запись:**\n"
        "   Просто напиши любое слово\n\n"
        "3️⃣ **Показать все из категории:**\n"
        "   /категория Название\n\n"
        "4️⃣ **Показать полностью:**\n"
        "   показать фрагмент Название\n\n"
        "5️⃣ **Изменить:**\n"
        "   Изменить фрагмент Название: Новый текст\n\n"
        "6️⃣ **Удалить:**\n"
        "   /удалить Название\n\n"
        "7️⃣ **Список категорий:**\n"
        "   /категории\n\n"
        "8️⃣ **Список названий:**\n"
        "   /названия\n\n"
        "⚠️ **Важно:** Названия должны быть уникальными!\n"
        "📌 Ты видишь только свои записи.",
        parse_mode="Markdown"
    )

@dp.message(Command("новый"))
async def new_lore(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    body = text.replace("/новый", "").strip()
    
    if ":" not in body:
        await message.answer("⚠️ Формат: /новый Категория | Название: Текст\nИли: /новый Название: Текст (без категории)")
        return
    
    title_part, content = body.split(":", 1)
    title_part = title_part.strip()
    content = content.strip()
    
    if "|" in title_part:
        category, title = title_part.split("|", 1)
        category = category.strip()
        title = title.strip()
    else:
        category = "Без категории"
        title = title_part
    
    if not title or not content:
        await message.answer("⚠️ Название и текст не могут быть пустыми!")
        return
    
    add_lore(user_id, category, title, content)
    await message.answer(
        f"✨ Сохранено!\n"
        f"📂 Категория: {category}\n"
        f"📌 {title}\n\n"
        f"Твоя вселенная становится глубже! 🌌"
    )

@dp.message(Command("категории"))
async def show_categories(message: types.Message):
    user_id = message.from_user.id
    categories = get_categories(user_id)
    
    if not categories:
        await message.answer("📭 У тебя пока нет категорий. Создай первую запись через /новый!")
        return
    
    answer = "📂 **Твои категории:**\n\n"
    for cat in categories:
        answer += f"• {cat}\n"
    
    await message.answer(answer, parse_mode="Markdown")

@dp.message(Command("названия"))
async def show_titles(message: types.Message):
    user_id = message.from_user.id
    titles = get_titles(user_id)
    
    if not titles:
        await message.answer("📭 У тебя пока нет записей. Создай первую через /новый!")
        return
    
    answer = "📌 **Твои записи (названия):**\n\n"
    for title in titles:
        answer += f"• {title}\n"
    answer += "\n💡 Используй эти названия для команд: показать фрагмент, изменить фрагмент, /удалить"
    
    await message.answer(answer, parse_mode="Markdown")

@dp.message(Command("категория"))
async def show_by_category(message: types.Message):
    user_id = message.from_user.id
    category = message.text.replace("/категория", "").strip()
    
    if not category:
        await message.answer("⚠️ Напиши: /категория Название_категории\nНапример: /категория Персонажи")
        return
    
    results = get_lore_by_category(user_id, category)
    
    if not results:
        await message.answer(f"📭 В категории «{category}» пока нет записей.")
        return
    
    answer = f"📂 **Категория: {category}**\n\n"
    for title, content, date in results:
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        preview = content[:100] + "..." if len(content) > 100 else content
        answer += f"📌 *{title}*\n📅 {formatted_date}\n{preview}\n\n"
    
    if len(answer) > 4000:
        answer = answer[:4000] + "\n... (много записей, уточни)"
    
    await message.answer(answer, parse_mode="Markdown")

@dp.message(Command("все"))
async def show_all(message: types.Message):
    user_id = message.from_user.id
    results = get_all_lore(user_id)
    
    if not results:
        await message.answer("📭 В хрониках пока пусто. Самое время написать первую главу!")
        return
    
    answer = "📜 **Полная хронология:**\n\n"
    for category, title, content, date in results:
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        preview = content[:150] + "..." if len(content) > 150 else content
        answer += f"📂 *{category}*\n📌 *{title}*\n📅 {formatted_date}\n{preview}\n\n"
    
    if len(answer) > 4000:
        answer = answer[:4000] + "\n... (много записей, используй поиск)"
    
    await message.answer(answer, parse_mode="Markdown")

@dp.message(Command("вдохновение"))
async def inspire(message: types.Message):
    user_id = message.from_user.id
    result = get_random_lore(user_id)
    
    if not result:
        await message.answer("📭 Ты еще не записал ни одного события. Напиши /новый и начни творить!")
        return
    
    title, content = result
    
    variants = [
        f"💡 Вспомни этот момент:\n\n*{title}*\n{content}\n\n🔥 А что случилось за 5 минут до этого? Может, пора это записать?",
        f"✨ Озарение!\n\n*{title}*\n{content}\n\n🌈 А что если посмотреть на это с другой стороны? Что изменится?",
        f"📖 Страница из твоей истории:\n\n*{title}*\n{content}\n\n⚔️ Как этот момент повлиял на дальнейшие события?",
        f"🎭 Взгляд из прошлого:\n\n*{title}*\n{content}\n\n🕯️ Может, это ключ к чему-то большему?",
        f"🌅 Твой мир оживает:\n\n*{title}*\n{content}\n\n🌟 Что было самым важным в этом моменте?",
        f"📜 Свиток найден:\n\n*{title}*\n{content}\n\n🔮 А что будет, если это событие произойдёт иначе?"
    ]
    
    await message.answer(random.choice(variants), parse_mode="Markdown")

@dp.message(Command("удалить"))
async def delete_lore_command(message: types.Message):
    user_id = message.from_user.id
    title = message.text.replace("/удалить", "").strip()
    
    if not title:
        await message.answer("⚠️ Напиши: /удалить Название фрагмента")
        return
    
    success = delete_lore(user_id, title)
    if success:
        await message.answer(
            f"🗑️ Фрагмент «{title}» удалён из хроник.\n"
            f"Эта история больше не часть вселенной... пока ты не решишь её вернуть. 🕯️"
        )
    else:
        await message.answer(
            f"😅 Я не нашёл фрагмент с названием «{title}».\n"
            f"Проверь название (регистр важен!)"
        )

@dp.message(Command("статистика"))
async def stats(message: types.Message):
    user_id = message.from_user.id
    total, categories = get_statistics(user_id)
    
    if total == 0:
        await message.answer("📭 В базе пока нет записей. Напиши /новый и начни творить!")
        return
    
    answer = "📊 **Статистика вселенной**\n\n"
    answer += f"📚 Всего фрагментов: *{total}*\n\n"
    answer += "📂 **По категориям:**\n"
    
    for category, count in categories:
        answer += f"• {category}: {count}\n"
    
    await message.answer(answer, parse_mode="Markdown")

# ============================================
#  ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================

@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # --- "показать фрагмент Название" ---
    if text.lower().startswith("показать фрагмент "):
        title = text[len("показать фрагмент "):].strip()
        
        if not title:
            await message.answer("⚠️ Напиши: показать фрагмент Название")
            return
        
        result = get_lore_by_title(user_id, title)
        if result:
            category, title, content, date = result
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
            await message.answer(
                f"📂 *{category}*\n"
                f"📌 *{title}*\n"
                f"📅 {formatted_date}\n\n"
                f"{content}",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"😅 Я не нашёл фрагмент с названием «{title}».\n"
                f"Проверь название (регистр важен!) или создай его через /новый"
            )
        return
    
    # --- "Изменить фрагмент Название: Новый текст" ---
    if text.lower().startswith("изменить фрагмент "):
        body = text[len("изменить фрагмент "):].strip()
        
        if ":" not in body:
            await message.answer("⚠️ Формат: Изменить фрагмент Название: Новый текст")
            return
        
        title, new_content = body.split(":", 1)
        title = title.strip()
        new_content = new_content.strip()
        
        if not title or not new_content:
            await message.answer("⚠️ Название и новый текст не могут быть пустыми!")
            return
        
        success = update_lore(user_id, title, new_content)
        if success:
            await message.answer(
                f"🌀 Временная линия переписана!\n"
                f"Сюжет «{title}» обновлён. Прошлое стёрто, да здравствует новое! 🌀"
            )
        else:
            await message.answer(
                f"😅 Я не нашёл фрагмент с названием «{title}».\n"
                f"Проверь название (регистр важен!)"
            )
        return
    
    # --- Обычный поиск ---
    results = search_lore(user_id, text)
    
    if not results:
        await message.answer(
            f"🔍 Я перерыл все свитки по запросу «{text}», но пока пусто...\n"
            f"Может, это знак, что пора придумать это событие и записать? ✍️"
        )
        return
    
    answer = f"🔍 **Нашлось по запросу «{text}»:**\n\n"
    for category, title, content, date in results:
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        preview = content[:150] + "..." if len(content) > 150 else content
        answer += f"📂 *{category}*\n📌 *{title}*\n📅 {formatted_date}\n{preview}\n\n"
    
    if len(answer) > 4000:
        answer = answer[:4000] + "\n... (много совпадений, уточни запрос)"
    
    await message.answer(answer, parse_mode="Markdown")

# ============================================
#  ЗАПУСК
# ============================================

async def main():
    init_db()
    print("🚀 Хранитель Лора запущен! Жду твоих записей...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())