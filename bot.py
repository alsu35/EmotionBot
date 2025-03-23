import asyncio
import json
import os
import random
import asyncio
import subprocess
import logging
import datetime
from telegram.ext import JobQueue
from pathlib import Path
from telegram.ext import filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, filters, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext, MessageHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import nest_asyncio

# токен
TOKEN = "7620764762:AAEcapfLboAOgmy7OBCShxUc84OSRFg3KDg"

# заголовок для теста
TEST_DESCRIPTION = (
    "Этот тест помогает определить выраженность тревожности в структуре личности.\n\n"
    "Тревожность как личностная черта означает мотив или приобретенную поведенческую позицию, "
    "которая заставляет человека воспринимать широкий круг объективно безопасных обстоятельств "
    "как содержащих угрозу, побуждая реагировать на них состояниями тревоги.\n\n"
    "Выберите действие:"
)
# рекомендации по настроению
EMOTION_ADVICE = {
    "Стресс": [
        (
            "🔄 Квадратное дыхание\n\n"
            "Инструкция:\n"
            "- Вдох через нос (4 сек)\n"
            "- Задержка (4 сек)\n"
            "- Выдох через рот (4 сек)\n"
            "- Пауза (4 сек)\n\n"
            "🔁 Цикл: 5-10 повторов\n"
            "💫 Эффект: Синхронизирует сердце и мозг"
        ),
        (
            "🚶 Антистресс-прогулка\n\n"
            "Рекомендации:\n"
            "- Идите в спокойном темпе\n"
            "- Отмечайте детали вокруг (деревья, облака)\n"
            "- Отключите телефон на 10 мин\n\n"
            "🌿 Эффект: Повышает окситоцин"
        )
    ],
    "Тревога": [
        (
            "🌀 Дыхание 4-7-8\n\n"
            "Инструкция:\n"
            "- Вдох через нос (4 сек)\n"
            "- Задержка дыхания (7 сек)\n"
            "- Выдох через рот (8 сек)\n\n"
            "💨 Повторите 4 цикла\n"
            "✨ Эффект: Снижает уровень адреналина\n"
            "Воспользуйся кнопкой Дыхательное упражнение, чтобы делать упражнения вместе!"
        ),
        (
            "📿 Медитация на дыхании\n\n"
            "Как выполнять:\n"
            "- Сядьте удобно, закройте глаза\n"
            "- Сосредоточьтесь на вдохах/выдохах\n"
            "- Считайте: «Вдох-1, выдох-2» (до 10)\n\n"
            "⏱ Длительность: 5-10 минут\n"
            "✨ Эффект: Снижает уровень кортизола"
        )
    ],
    "Усталость": [
        (
            "💤 Техника «Кофе-нап»\n\n"
            "Как выполнять:\n"
            "- Выпейте чашку кофе (без сахара)\n"
            "- Сразу лягте поспать на 15-20 мин\n"
            "- Проснитесь до фазы глубокого сна\n\n"
            "⚠️ Предупреждение: Не подходит при гипертонии"
        ),
        (
            "🎧 Звуковая терапия\n\n"
            "Примеры треков:\n"
            "- Шум прибоя (10-часовой loop)\n"
            "- Пение китов (Calm, Headspace)\n\n"
            "🔊 Как использовать:\n"
            "- Включите фоном во время работы\n"
            "- Слушайте в наушниках для погружения\n"
            "❕Воспользуйся кнопкой Релаксация, чтобы уже начать слушать музыку для расслабления!"
        )
    ],
    "Гнев": [
        (
            "💥 Техника «Бумажный гнев»\n\n"
            "Инструкция:\n"
            "- Скомкайте лист бумаги\n"
            "- Разорвите его на мелкие кусочки\n"
            "- Выбросьте в урну с мыслью: «Гнев уходит»\n\n"
            "🔥 Альтернатива: Побить подушку"
        ),
        (
            "❄️ Дыхание «Охлаждение»\n\n"
            "Как выполнять:\n"
            "- Вдох через нос (3 сек)\n"
            "- Выдох через сложенные трубочкой губы (6 сек)\n\n"
            "⏱ 10 циклов → снижает импульсивность"
        )
    ],
    "Одиночество": [
        (
            "🤝 Виртуальный челлендж\n\n"
            "Что делать:\n"
            "- Напишите 3 людям с вопросом «Как твои дела?»\n"
            "- Примите участие в онлайн-ивентах (вебинары, игры)\n\n"
            "🌐 Примеры: Meetup, Discord-сообщества"
        ),
        (
            "📝 Письмо будущему себе\n\n"
            "Шаблон:\n"
            "- «Через год я буду...»\n"
            "- «Сейчас мне важно помнить, что...»\n\n"
            "✉️ Отправьте письмо через сервис FutureMe"
        )
    ],
    "Апатия": [
        (
            "🚀 Микроцели\n\n"
            "Примеры:\n"
            "- Сделать 5-минутную зарядку\n"
            "- Приготовить чай с любимой добавкой\n\n"
            "✅ Каждая выполненная задача → шаг к выходу из апатии"
        ),
        (
            "🎭 Техника «Актёр»\n\n"
            "Инструкция:\n"
            "- Представьте, что вы играете энергичного персонажа\n"
            "- Действуйте «как будто» 15 минут\n\n"
            "🎯 Эффект: Запускает обратную связь мозг-тело"
        )
    ],
    "Радость": [
        (
            "🎉 Техника «Капсула счастья»\n\n"
            "Что делать:\n"
            "- Запишите на бумаге момент, когда вы чувствовали радость\n"
            "- Положите в банку и перечитывайте в трудные дни\n\n"
            "📦 Эффект: Создает «банк» позитивных воспоминаний"
        ),
        (
            "🌞 Ритуал благодарности\n\n"
            "Примеры:\n"
            "- Назовите 3 вещи, за которые благодарны сегодня\n"
            "- Поделитесь благодарностью с близким человеком\n\n"
            "💫 Почему работает: Смещает фокус на позитив"
        )
    ],
    "Спокойствие": [
        (
            "🕯️ Практика «Чайная церемония»\n\n"
            "Инструкция:\n"
            "- Приготовьте чай осознанно: наблюдайте за цветом, паром, ароматом\n"
            "- Пейте медленно, концентрируясь на вкусе\n\n"
            "🍵 Эффект: Замедляет ритм, снижает тревожность"
        ),
        (
            "🌀 Дыхание 4-7-8\n\n"
            "Инструкция:\n"
            "- Вдох через нос (4 сек)\n"
            "- Задержка дыхания (7 сек)\n"
            "- Выдох через рот (8 сек)\n\n"
            "💨 Повторите 4 цикла\n"
            "✨ Эффект: Балансирует нервную систему\n"
            "❕Воспользуйся кнопкой Дыхательное упражнение, чтобы делать упражнения вместе!"
        )
    ],
    "Вдохновение": [
        (
            "🚀 Метод «Случайный вход»\n\n"
            "Действия:\n"
            "- Откройте книгу на случайной странице → прочтите абзац\n"
            "- Включите радио → запишите первую услышанную фразу\n\n"
            "🎲 Почему работает: Стимулирует ассоциативное мышление"
        ),
        (
            "📸 Фото-челлендж «Новый взгляд»\n\n"
            "Задание:\n"
            "- Сфотографируйте 5 обычных предметов необычным способом\n"
            "- Поделитесь с другом или в соцсетях\n\n"
            "🔍 Эффект: Развивает креативность"
        )
    ],
    "Уверенность": [
        (
            "💪 Практика «Поза супергероя»\n\n"
            "Инструкция:\n"
            "- Встаньте прямо, руки на бедрах, подбородок приподнят\n"
            "- Удерживайте позу 2 минуты\n\n"
            "🦸 Эффект: Повышает уровень тестостерона"
        ),
        (
            "📖 Аффирмации для уверенности\n\n"
            "Примеры:\n"
            "- «Я справлялся с трудностями раньше — справлюсь и сейчас»\n"
            "- «Мое мнение важно»\n\n"
            "🔁 Произносите вслух перед зеркалом"
        )
    ]

}
# перевод настроения человека
EMOTION_MAPPING = {
    "anxiety": "Тревога",
    "stress": "Стресс",
    "fatigue": "Усталость",
    "anger": "Гнев",
    "loneliness": "Одиночество",
    "apathy": "Апатия",
    "worry": "Беспокойство", 
    "overload": "Перегрузка",
    "confidence": "Уверенность",
    "inspiration": "Вдохновение",
    "calm": "Спокойствие",
    "joy": "Радость"
}

# вопросы по тесту
SPIELBERGER_QUESTIONS = [
    # ситуативная тревожность (1-20)
    "1. Я спокоен",
    "2. Мне ничто не угрожает",
    "3. Я нахожусь в напряжении",
    "4. Я внутренне скован",
    "5. Я чувствую себя свободно",
    "6. Я расстроен",
    "7. Меня волнуют возможные неудачи",
    "8. Я ощущаю душевный покой",
    "9. Я встревожен",
    "10. Я испытываю чувство внутреннего удовлетворения",
    "11. Я уверен в себе",
    "12. Я нервничаю",
    "13. Я не нахожу себе места",
    "14. Я взвинчен",
    "15. Я не чувствую скованности, напряжения",
    "16. Я доволен",
    "17. Я озабочен",
    "18. Я слишком возбужден и мне не по себе",
    "19. Мне радостно",
    "20. Мне приятно",
    # личностная тревожность (21-40)
    "21. У меня бывает приподнятое настроение",
    "22. Я бываю раздражительным",
    "23. Я легко расстраиваюсь",
    "24. Я хотел бы быть таким же удачливым, как и другие",
    "25. Я сильно переживаю неприятности и долго не могу о них забыть",
    "26. Я чувствую прилив сил и желание работать",
    "27. Я спокоен, хладнокровен и собран",
    "28. Меня тревожат возможные трудности",
    "29. Я слишком переживаю из-за пустяков",
    "30. Я бываю вполне счастлив",
    "31. Я все принимаю близко к сердцу",
    "32. Мне не хватает уверенности в себе",
    "33. Я чувствую себя беззащитным",
    "34. Я стараюсь избегать критических ситуаций и трудностей",
    "35. У меня бывает хандра",
    "36. Я бываю доволен",
    "37. Всякие пустяки отвлекают и волнуют меня",
    "38. Бывает, что я чувствую себя неудачником",
    "39. Я уравновешенный человек",
    "40. Меня охватывает беспокойство, когда я думаю о своих делах и заботах"
]

ANSWER_OPTIONS = [
    ("Никогда", "0"),
    ("Почти никогда", "1"),
    ("Часто", "2"),
    ("Почти всегда", "3")
]

# ключ для преобразования ответов
INVERTED_QUESTIONS = [1, 2, 5, 8, 10, 11, 15, 16, 19, 20, 21, 26, 27, 30, 36, 39]

# кнопки на клавиатуре
keyboard = [
        ["💨 Дыхательное упражнение", "💡 Совет для успокоения"],
        ["📝 Тест на тревожность", "🎧 Релаксация"],
        ["🌱 Выбрать эмоцию", "⚙️ Уведомления об отдыхе"]]


# словарь для хранения настроек уведомлений пользователей
user_notifications = {}

# инициализация планировщика
scheduler = AsyncIOScheduler()

# приветствие
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user.first_name
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        f"Привет, {user}! Я бот для эмоциональной разгрузки.Давай вместе снизим стресс и тревожность.😊 Вот что я умею:\n\n"
        "💨 дыхательное упражнение\n"
        "💡 советы для успокоения\n"
        "📝 тест на уровень тревожности\n\n"
        "Выберите действие с помощью кнопок на клавиатуре ⬇️",
        reply_markup = reply_markup
    )
    
    
# обработчик для кнопок на клав
async def handle_buttons(update: Update, context: CallbackContext):
    text = update.message.text

    if text == "💨 Дыхательное упражнение":
        await guided_breathing_start(update, context)
    elif text == "💡 Совет для успокоения":
        await random_advice(update, context)
    elif text == "📝 Тест на тревожность":
        await anxiety_test(update, context)
    elif text == "🎧 Релаксация":
        await audio_menu(update, context)
    elif text == "🌱 Выбрать эмоцию": 
        await emotion_selection(update, context)
    elif text == "⚙️ Уведомления об отдыхе":
        await settings_menu(update, context)

# обработчик для дых упражнения
async def guided_breathing(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text("Вдохните через нос на 4 секунды... 😌")
    await asyncio.sleep(3)

    await query.message.edit_text("Задержите дыхание на 7 секунд... ⏳")
    await asyncio.sleep(6)

    await query.message.edit_text("Медленно выдохните через рот на 8 секунд... 🌬️")
    await asyncio.sleep(7)

    await query.message.edit_text("Отлично! Повторите 4 раза для максимального эффекта.")
        
async def audio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🌧 Дождь", callback_data="audio_rain")],
        [InlineKeyboardButton("🌲 Лес", callback_data="audio_forest")]
    ]
    await update.message.reply_text(
        "🎧 Выберите звуковую терапию:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
# база аудиофайлов
AUDIO_LIBRARY = {
    "rain": {
        "file": os.path.abspath(os.path.join("music", "rain.mp3")), 
        "duration": 53
    },
    "forest": {
        "file": os.path.abspath(os.path.join("music", "forest.mp3")),
        "duration": 329
    }
}

async def play_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    sound_key = query.data.split("_")[1]

    if sound_key not in AUDIO_LIBRARY:
        await query.message.reply_text("Ошибка: Аудиофайл не найден в базе.")
        return

    audio_file = AUDIO_LIBRARY[sound_key]["file"] 

    # print(f"🔍 Проверка пути: {audio_file}")

    if not os.path.exists(audio_file):
        await query.message.reply_text(f"Ошибка: Аудиофайл не найден по пути {audio_file}.")
        return

    await query.answer()
    await query.message.reply_text(f"🎶 Подождите пока отправится {sound_key} и наслаждайтесь музыкой!")

    with open(audio_file, "rb") as audio:
        await query.message.reply_audio(audio=audio)
        
        
        
# заголовок к дых упражнению
async def guided_breathing_start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Далее ▶️", callback_data="start_breathing")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Приготовьтесь к дыхательному упражнению. \n\n"
        "Я буду отсчитывать время, а вы выполняйте упражнение. \n\n"
        "Начнем!🔥",
        reply_markup=reply_markup
    )

# случайный совет
async def random_advice(update, context):
    try:
        db_path = Path(__file__).parent / "motivation_db.json"
        
        with open(db_path, "r", encoding="utf-8") as f:
            advice_list = json.load(f)
        
        advice = random.choice(advice_list)
        author = f"\n — {advice['author']}" if advice.get("author") else ""
        quote = f"📌 {advice['text']}{author}"
        
    except FileNotFoundError:
        quote = "⚠️ Файл с советами не найден!"
    except json.JSONDecodeError:
        quote = "⚠️ Ошибка в формате файла!"
    except Exception as e:
        quote = f"⚠️ Ошибка: {str(e)}"
    
    await update.message.reply_text(quote)

# упражнения по состоянию человека
async def emotion_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Тревога", callback_data="emotion_anxiety"),
         InlineKeyboardButton("Стресс", callback_data="emotion_stress")],
        [InlineKeyboardButton("Усталость", callback_data="emotion_fatigue"),
         InlineKeyboardButton("Гнев", callback_data="emotion_anger")],
        [InlineKeyboardButton("Одиночество", callback_data="emotion_loneliness"),
         InlineKeyboardButton("Апатия", callback_data="emotion_apathy")],
        [InlineKeyboardButton("Уверенность", callback_data="emotion_confidence"),
         InlineKeyboardButton("Вдохновение", callback_data="emotion_inspiration")],
        [InlineKeyboardButton("Спокойствие", callback_data="emotion_calm"),
         InlineKeyboardButton("Радость", callback_data="emotion_joy")]
    ]
    await update.message.reply_text(
        "📌 Выберите ваше текущее состояние:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# обработчики упражнений по состоянию
async def handle_emotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    emotion_key = query.data.split("_")[1] 

    emotion = EMOTION_MAPPING.get(emotion_key, None)

    if emotion is None:
        await query.message.edit_text("⚠️ Ошибка: неизвестная эмоция!")
        return

    advice = random.choice(EMOTION_ADVICE[emotion])

    await query.message.edit_text(
        f"🌟 Рекомендации при {emotion}:\n\n{advice}"
    )

# обработчики теста
async def anxiety_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["test_step"] = 0
    context.user_data["scores"] = []
    keyboard = [[InlineKeyboardButton("Начать тест", callback_data="start_test")]]
    await update.message.reply_text("Этот тест помогает определить уровень тревожности. Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data["test_step"]
    
    if step >= len(SPIELBERGER_QUESTIONS):
        await finish_test(update, context)
        return
    
    buttons = [[InlineKeyboardButton(text, callback_data=value)] for text, value in ANSWER_OPTIONS]
    if step > 0:
        buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="prev_question")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    text = f"Вопрос {step+1}/{len(SPIELBERGER_QUESTIONS)}:\n{SPIELBERGER_QUESTIONS[step]}"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_test":
        await send_question(update, context)
        return
    
    if query.data == "prev_question":
        if context.user_data["test_step"] > 0:
            context.user_data["test_step"] -= 1
        await send_question(update, context)
        return
    
    step = context.user_data["test_step"]
    raw_score = int(query.data)
    score = 4 - raw_score if (step + 1) in INVERTED_QUESTIONS else raw_score + 1
    context.user_data["scores"].append(score)
    
    context.user_data["test_step"] += 1
    await send_question(update, context)

def get_anxiety_level(score):
    if score < 12:
        return "очень низкая"
    elif 12 <= score <= 30:
        return "низкая"
    elif 31 <= score <= 44:
        return "умеренная"
    else:
        return "высокая"

async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = context.user_data.get("scores", [])
    st_score = sum(scores[:20])
    lt_score = sum(scores[20:])
    
    def get_description(score, type_name):
        level = get_anxiety_level(score)
        text = ""
        
        # советы для СТ и ЛТ внутри каждого уровня
        if level == "очень низкая":
            if type_name == "Ситуативная тревожность":
                text = (
                    "⚠️ Состояние апатии или отрицание стресса. Совет: "
                    "🧘 Техники «здесь и сейчас»: дыхательные упражнения (например, 4-7-8), прогрессивная мышечная релаксация."
                    "📝 Планирование: разбить задачу на этапы, составить четкий план действий."
                    "⏳ Ограничение времени на тревогу: выделить 10–15 минут в день на анализ переживаний."
                )
            else:  # личностная
                text = (
                    "🔍 Возможна подавленная тревога или низкая самооценка. "
                    "Рекомендуется: ведение дневника эмоций, консультация психолога."
                )
                
        elif level == "низкая":
            if type_name == "Ситуативная тревожность":
                text = "🌤 Нормальная реакция. Для поддержания баланса: практикуйте осознанность."
            else:
                text = (
                    "🔅 Склонность избегать сложных ситуаций. "
                    "Совет: постепенно расширяйте зону комфорта."
                )
                
        elif level == "умеренная":
            text = (  # общий совет
                "✅ Полезный уровень для продуктивности. "
                "Рекомендуется: регулярный самоанализ, баланс работы и отдыха."
            )
            
        else:  # высокая
            if type_name == "Ситуативная тревожность":
                text = (
                    "🚨 Острый стресс. Срочные меры: дыхание 4-7-8, "
                    "физическая активность, разговор с близкими."
                )
            else:
                text = (
                    "🔥 Хроническая тревога. Долгосрочно: КПТ-техники, "
                    "работа с установками, консультация специалиста."
                )
                
        return f"{type_name}: {score} ({level})\n{text}\n"

    result_text = (
        "🔍 Результаты:\n\n"
        f"{get_description(st_score, 'Ситуативная тревожность')}\n"
        f"{get_description(lt_score, 'Личностная тревожность')}\n"
        "📌 Примечание:\n"
        "- Ситуативная тревожность: временное состояние, зависит от контекста\n"
        "- Личностная: устойчивая черта, требует системной работы"
    )
    
    await update.effective_chat.send_message(text=result_text)

nest_asyncio.apply()
    
# функция для отправки уведомлений
async def send_notification(user_id, context):
    message = (
        "✨ Время сделать перерыв! ✨\n\n"
        "😌 Расслабься и удели минутку дыхательному упражнению.\n"
        "🌿 Это поможет снизить стресс и улучшить концентрацию.\n\n"
        "💙 Нажми кнопку ниже, чтобы начать ⬇️"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("▶️ Начать дыхание", callback_data="start_breathing")]]
    )

    try:
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)
        # print(f"✅ Напоминание отправлено пользователю {user_id}")
    except Exception as e:
        print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")

# для передачи параметров в send_notification
def notification_wrapper(user_id, context):
    async def wrapper():
        await send_notification(user_id, context)
    return wrapper

# функция для настройки уведомлений
async def settings_menu(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton("🔔 Каждые 2 часа", callback_data="every_2_hours")],
        [InlineKeyboardButton("🌞 Утром и вечером", callback_data="morning_evening")],
        [InlineKeyboardButton("❌ Отключить уведомления", callback_data="disable_notifications")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Настройте напоминания о заботе о себе! 🌸\nВыберите частоту уведомлений: 🕒",
        reply_markup=reply_markup
    )

# обработчик выбора уведомлений
async def handle_notification_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data

    if scheduler.get_job(str(user_id)):
        scheduler.remove_job(str(user_id))
    if scheduler.get_job(f"{user_id}_morning"):
        scheduler.remove_job(f"{user_id}_morning")
    if scheduler.get_job(f"{user_id}_evening"):
        scheduler.remove_job(f"{user_id}_evening")

    if choice == "every_2_hours":
        scheduler.add_job(notification_wrapper(user_id, context), "interval", hours=2, name=str(user_id))
        user_notifications[user_id] = "каждые 2 часа"
        await query.answer("✅ Уведомления включены (каждые 2 часа).")

    elif choice == "morning_evening":
        scheduler.add_job(notification_wrapper(user_id, context), "cron", hour=10, minute=0, name=f"{user_id}_morning")
        scheduler.add_job(notification_wrapper(user_id, context), "cron", hour=16, minute=0, name=f"{user_id}_evening")
        user_notifications[user_id] = "утром и вечером"
        await query.answer("✅ Уведомления включены (утром и вечером).")

    elif choice == "disable_notifications":
        user_notifications.pop(user_id, None)
        await query.answer("❌ Уведомления отключены.")

async def main():
    scheduler.start()
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons)) 
    
    # обработчик для дыхательного упражнения
    app.add_handler(CallbackQueryHandler(guided_breathing, pattern="start_breathing"))
    
    # обработчики для теста
    app.add_handler(CallbackQueryHandler(handle_test_answer, pattern="start_test|prev_question|^[0-3]$"))
    
    # обработчики для упражнений по состоянию
    app.add_handler(CallbackQueryHandler(handle_emotion, pattern="^emotion_"))
    
    # обработчики для музыки
    app.add_handler(CommandHandler("audio", audio_menu))
    app.add_handler(CallbackQueryHandler(play_audio, pattern="^audio_"))
    
    
    # обработчики для уведомлений
    
    app.add_handler(CommandHandler("settings", settings_menu))
    app.add_handler(CallbackQueryHandler(handle_notification_choice))
    

    await app.run_polling()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  
