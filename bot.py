import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
CHANNEL_LINK = "ссылка"  # Замените на реальную ссылку на канал
ELENA_CONTACT = "@Lebedeva_Elen"
ADMIN_CHAT_ID = 269435099  # chat_id администратора

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Импортируем тестовый роутер
from test_module import test_router

# Функции для работы с базой данных
async def get_db_connection():
    try:
        return await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

async def init_database():
    """Создание таблиц при запуске бота"""
    conn = await get_db_connection()
    if not conn:
        return

    try:
        # Создание таблицы пользователей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS mss_users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Создание таблицы сообщений
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS mss_chat (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                username VARCHAR(255),
                message_text TEXT,
                message_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        logging.info("Database tables initialized successfully")

    except Exception as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        await conn.close()

async def add_user_to_db(user: types.User):
    """Добавление пользователя в БД"""
    conn = await get_db_connection()
    if not conn:
        return

    try:
        await conn.execute('''
            INSERT INTO mss_users (user_id, username, first_name, last_name, last_activity)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id)
            DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                last_activity = EXCLUDED.last_activity
        ''', user.id, user.username, user.first_name, user.last_name, datetime.now())

    except Exception as e:
        logging.error(f"Error adding user to database: {e}")
    finally:
        await conn.close()

async def log_message_to_db(user: types.User, message_text: str, message_type: str = "text"):
    """Логирование сообщения в БД"""
    conn = await get_db_connection()
    if not conn:
        return

    try:
        await conn.execute('''
            INSERT INTO mss_chat (user_id, username, message_text, message_type)
            VALUES ($1, $2, $3, $4)
        ''', user.id, user.username, message_text, message_type)

    except Exception as e:
        logging.error(f"Error logging message to database: {e}")
    finally:
        await conn.close()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📚 Узнать о курсе"), KeyboardButton(text="👥 Для какого возраста")],
        [KeyboardButton(text="📋 Формат занятий"), KeyboardButton(text="🎯 Результаты курса")],
        [KeyboardButton(text="⏰ Как проходят занятия"), KeyboardButton(text="💰 Оплата")],
        [KeyboardButton(text="🆘 Связаться с поддержкой"), KeyboardButton(text="🧩 Мини тест")]
    ], resize_keyboard=True)

def get_support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 Связаться с поддержкой", callback_data="support")]
    ])

class SupportStates(StatesGroup):
    waiting_for_question = State()

@dp.message(CommandStart())
async def start_handler(message: Message):
    # Добавляем пользователя в БД
    await add_user_to_db(message.from_user)

    # Логируем команду /start
    await log_message_to_db(message.from_user, "/start", "command")

    welcome_text = f"""Здравствуйте! Добро пожаловать!

Я – Елена Лебедева, а это – официальный бот курса "Излагай ясно" для подростков и взрослых.

Здесь я расскажу вам подробно о самом курсе и его особенностях.

Чтобы не потеряться, подписывайтесь на мой канал {CHANNEL_LINK}

Если у вас возникнут вопросы, пожалуйста, нажмите на кнопку «Связаться с поддержкой»."""

    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == "📚 Узнать о курсе")
async def handle_about_course(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    course_text = """📚 Узнать подробнее о курсе "Излагай ясно"

Курс по развитию устной и письменной речи.

Курс подойдет вам, если вы задаетесь вопросами:
• Как научить ребенка писать?
• Что нужно писать во вступлении, в основной части, в заключении
• Как преодолеть трудности при написании творческих письменных работ
• Что делать, если любая письменная работа ввергает в уныние
• Как помочь ребенку оформить свои мысли письменно, хотя нет сложности что-то рассказать
• Как не боятся выражать свои мысли на бумаге

На курсе "Излагай ясно" ребенок, а при желании и родитель,
📝 освоит алгоритм создания текстов
📖 расширит словарный запас
🎤 отточит искусство пересказа
✍️ научится применять стилистические техники
🔍 поймет, как выделять ключевые слова и идеи в тексте
📄 напишет 20 собственных текстов

Курс включает в себя:

— 9 полноценных разделов теоретической информации
— 24 практических занятий
— 20 собственных текстов, которые напишет ученик
— Сопровождение в чате в течение всего курса (обратная связь к заданиям, ответы на вопросы)
— Полезные дополнительные материалы (остаются у вас после окончания курса)

📌 Все продумано для того, чтобы каждый участник мог получить свой результат, а также максимум пользы от общения с ведущим и «сокурсниками»."""

    await message.answer(course_text)

@dp.message(lambda message: message.text == "👥 Для какого возраста")
async def handle_age_info(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    age_text = """👥 Для какого возраста курс?

Курс «Излагай ясно» для подростков 9-16 лет.

Задумывались ли о том, что отличает умного, преуспевающего и известного человека?

Умение четко и ясно формулировать свои мысли, выделять главное и передавать этот смысл другим. Этот навык можно начинать тренировать с раннего подросткового возраста с помощью письменных практик.

Такому, как оказалось, не учат в школе. А начинается это умение с выделения ключевых слов в тексте, пересказа, письменных практик – базы для дальнейшего структурирования собственных мыслей и изложения их на бумаге.

Курс посвящен писательской «азбуке» – основам развития навыков письменной речи у детей. Ученики фокусируются на том, КАК писать, а не на то, ЧТО писать.

Уроки развития письменной речи – это основа основ и для структурирования мышления. После прохождения курса за любыми текстами ученик начнет видеть их структуру, различать жанры, моментально выделять главное, выделяя суть, не отвлекаясь на детали и украшения.

На этом фундаменте строится все здание искусства письма.

👶 Возраст участников Курса: 9-16 лет
🤝 Ребятам 9-11 лет курс рекомендовано проходить вместе со взрослым
🎓 Ребята 12-16 лет и взрослые работают самостоятельно

Курс (доступ на 10 месяцев) включает:
• 9 полноценных разделов теоретической информации
• 24 практических занятий онлайн
• Сопровождение участника в чате
• 20 собственных текстов, которые напишет ученик
• Полезные дополнительные материалы"""

    await message.answer(age_text)

@dp.message(lambda message: message.text == "📋 Формат занятий")
async def handle_format_info(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    format_text = """📋 Какой формат занятий?

24 "живые" групповые встречи онлайн. Запись будет.

Групповой формат занятий:
• обогатит каждого участника новыми и интересными идеями
• позволит учиться на чужом опыте
• улучшит навык активного слушания и внимания к деталям

При этом каждый участник получит индивидуальную обратную связь по написанным текстам."""

    await message.answer(format_text)

@dp.message(lambda message: message.text == "🎯 Результаты курса")
async def handle_results_info(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    results_text = """🎯 Что ребенок будет знать и уметь к концу курса?

«Мне не дано писать сочинение», — так никогда не скажет ученик полностью освоивший все 9 структур курса "Излагай ясно".

На курсе ученик научится работать с текстом, с разными типами и структурами текстов, познакомится с приемами украшения текста и, конечно, научиться последовательно и своевременно применять изученное.

Шаг за шагом мы пройдем путь написания сочинений от самых простых до сложных форм, состоящих из нескольких абзацев.

✅ Построение текста перестанет быть мучительной загадкой!
✅ Вам станет понятно, а главное достижимо писать тексты, даже если совсем нет вдохновения и мыслей, как это делать.

📚 9 разделов, которые будут разобраны на курсе:

1. Заметки и опорная схема
2. Отбор ключевых слов из каждого предложения
3. Пересказ исходного текста по опорной схеме
4. Составление текста
5. Краткое письменное изложение исходного текста по опорной схеме
6. Творческое изложение нарратива
7. Ключевые слова - ответы на вопросы плана нарратива
8. Сжатое изложение справочной статьи
9. Ключевые слова - факты, отобранные из одного источника. Модель «тема — скрепа»

И многое другое...

Ученик овладеет основными жанрами учебных письменных текстов:
• изложением
• сочинением-описанием
• сочинением-рассуждением
• сочинением на свободную тему
• докладом
• рефератом
• эссе, в том числе отзывом на литературное произведение

Кроме того, он научится хорошо понимать разницу между типами и стилями речи, практически применять множество элементов структуры и стиля и разнообразные средства художественной выразительности текста."""

    await message.answer(results_text)

@dp.message(lambda message: message.text == "⏰ Как проходят занятия")
async def handle_schedule_info(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    schedule_text = """⏰ Как проходят занятия?

👥 до 10 человек в группе
⏱ 90 мин раз в неделю
📅 в понедельник или четверг 10.00 по МСК (10.00-11.30)
📅 в субботу 16.00 по МСК (16.00-17.30)

📚 Какие понадобятся учебники
Все необходимые материалы для работы на курсе будут предоставлены в электронном виде

Дополнительно к курсу вы можете приобрести следующие учебники (ссылки на магазин КБ):
• Силлабус
• Уроки развития речи
• Тетрадь учителя
• Тетрадь ученика
• "Плакаты в миниатюре"

📖 Что будет на занятиях:
• чтение текстов, подготовленных ребятами за неделю
• повтор материала предыдущих уроков
• историческая справка
• изучение нового материала по структуре
• чтение нового исходного текста, составление по нему опорной схемы и пересказ текста по опорным словам
• разбор новой стилистической техники и выполнение упражнений на новую и повторение пройденных стилистических техник
• работа с редкими словами

🏠 Как работать в течение недели дома?
Каждую неделю задание - написать сочинение по заданной структуре с использованием изученных стилистических техник

День 1 (день занятия): Составить опорную схему.
День 2: Пересказать текст по собственной опорной схеме. Написать первую рукопись по опорной схеме.
День 3: Редактировать рукопись и внести в текст все элементы из карты контроля.
День 4: Переписать работу начисто, при желании добавить иллюстрацию.

🎯 На чем фокус курса?
• на том КАК писать, а не что писать
• на текстах, структуре, стиле, а не на орфографии и пунктуации
• при необходимости проводятся индивидуальные занятия с разбором ошибок

🏰 Уроки развития речи курса "Излагай ясно" в этом году посвящены Средневековью. Совместим словесность и историю."""

    await message.answer(schedule_text)

@dp.message(lambda message: message.text == "💰 Оплата")
async def handle_payment_info(message: Message):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    payment_text = f"""💰 Как оплатить?

💳 Оплата:
• блоками по 6 занятий - 7200 р
• всего 4 блока по 7200 р каждый блок
• полная стоимость курса 28800 р

⚠️ ВНИМАНИЕ!
По поводу оплаты и любое другое общение может происходить только с личного аккаунта ведущего: {ELENA_CONTACT}

💳 Оплата производится на карту по номеру телефона на Сбер
📱 После оплаты нужно прислать скрин в личные сообщения.
🧾 Вам будет выслан чек об оплате.

📄 Договор оферты
Договор оферты содержит все необходимые условия предоставления услуг по курсу "Излагай ясно".

⚠️ Внимательно ознакомьтесь с условиями договора перед оплатой курса.

📞 Если у вас есть вопросы по договору, обратитесь к ведущему курса."""

    await message.answer(payment_text)


@dp.message(lambda message: message.text == "🆘 Связаться с поддержкой")
async def handle_support_button(message: Message, state: FSMContext):
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "menu_button")
    support_text = """🆘 Связаться с поддержкой

Опишите кратко ваш вопрос, и мы ответим вам сразу, как только сможем!

Напишите ваш вопрос следующим сообщением:"""

    await message.answer(support_text)
    await state.set_state(SupportStates.waiting_for_question)

@dp.callback_query(lambda c: c.data == "support")
async def process_support_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    support_text = """🆘 Связаться с поддержкой

Опишите кратко ваш вопрос, и мы ответим вам сразу, как только сможем!

Напишите ваш вопрос следующим сообщением:"""

    await callback_query.message.answer(support_text)
    await state.set_state(SupportStates.waiting_for_question)

@dp.message(SupportStates.waiting_for_question)
async def process_support_question(message: Message, state: FSMContext):
    # Добавляем пользователя в БД
    await add_user_to_db(message.from_user)
    # Логируем вопрос поддержки
    await log_message_to_db(message.from_user, message.text, "support_question")

    user_question = message.text
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    user_name = message.from_user.full_name

    # Отправляем вопрос Елене
    support_message = f"""🆘 Новый вопрос от пользователя бота:

👤 От: {user_name} ({user_info})
📝 Вопрос: {user_question}

Отправлено: {message.date.strftime('%d.%m.%Y %H:%M')}"""

    try:
        # Отправляем сообщение администратору
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=support_message)

        confirmation_text = f"""✅ Ваш вопрос получен и отправлен ведущему курса!

📝 Вопрос: {user_question}

👤 От: {user_name} ({user_info})

⏰ Елена ответит вам в ближайшее время!

📞 Для срочных вопросов обращайтесь напрямую: {ELENA_CONTACT}"""

    except Exception as e:
        logging.error(f"Failed to send message to admin: {e}")
        confirmation_text = f"""✅ Ваш вопрос получен!

📝 Вопрос: {user_question}

👤 От: {user_name} ({user_info})

⚠️ Возникла техническая проблема с автоматической отправкой.
📞 Пожалуйста, обратитесь напрямую к ведущему курса: {ELENA_CONTACT}"""

    await message.answer(confirmation_text)
    await state.clear()

@dp.message()
async def handle_other_messages(message: Message):
    # Проверяем, не является ли это сообщением для теста (обрабатывается в test_router)
    if message.text and "🧩 Мини тест" in message.text:
        return

    # Добавляем пользователя в БД
    await add_user_to_db(message.from_user)
    # Логируем любое другое сообщение
    await log_message_to_db(message.from_user, message.text, "other_message")

    help_text = f"""❓ Используйте меню для навигации по боту или обратитесь за помощью к ведущему курса: {ELENA_CONTACT}"""
    await message.answer(help_text, reply_markup=get_main_keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)

    # Подключаем роутер для тестов
    dp.include_router(test_router)

    # Инициализация базы данных при запуске
    await init_database()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())