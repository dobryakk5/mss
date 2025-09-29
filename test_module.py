import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Роутер для тестов
test_router = Router()

# --- FSM States для теста ---
class TestStates(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()

# --- Клавиатуры ---
start_test_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧩 Пройти тест")]],
    resize_keyboard=True
)

q1_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ Зимой лес спит")],
        [KeyboardButton(text="2️⃣ Жизнь в лесу продолжается")],
        [KeyboardButton(text="3️⃣ Лес красивый")]
    ],
    resize_keyboard=True
)

q2_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ Устно")],
        [KeyboardButton(text="2️⃣ Письменно")],
        [KeyboardButton(text="3️⃣ Одинаково")]
    ],
    resize_keyboard=True
)

q3_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сочинение")],
        [KeyboardButton(text="Пересказ")],
        [KeyboardButton(text="Квадрат")]
    ],
    resize_keyboard=True
)

q4_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ Начать")],
        [KeyboardButton(text="2️⃣ Продолжить (основная часть)")],
        [KeyboardButton(text="3️⃣ Закончить")]
    ],
    resize_keyboard=True
)

def get_main_keyboard_with_test():
    """Возвращает основное меню с добавленной кнопкой теста"""
    from bot import get_main_keyboard
    return get_main_keyboard()

# --- Функции для работы с БД ---
async def log_test_result_to_db(user, answers, level):
    """Логирование результатов теста в БД"""
    try:
        from bot import get_db_connection
        conn = await get_db_connection()
        if not conn:
            return

        answers_text = f"Q1: {answers.get('q1', 'N/A')}, Q2: {answers.get('q2', 'N/A')}, Q3: {answers.get('q3', 'N/A')}, Q4: {answers.get('q4', 'N/A')}, Q5: {answers.get('q5', 'N/A')}"

        await conn.execute('''
            INSERT INTO mss_chat (user_id, username, message_text, message_type)
            VALUES ($1, $2, $3, $4)
        ''', user.id, user.username, f"Результат теста - Уровень: {level}. Ответы: {answers_text}", "test_result")

    except Exception as e:
        logging.error(f"Error logging test result to database: {e}")
    finally:
        if conn:
            await conn.close()

# --- Хэндлеры ---
@test_router.message(F.text == "🧩 Пройти тест уровня")
async def start_test(message: Message, state: FSMContext):
    from bot import add_user_to_db, log_message_to_db
    await add_user_to_db(message.from_user)
    await log_message_to_db(message.from_user, message.text, "test_start")

    await state.clear()
    await state.set_state(TestStates.question1)

    await message.answer(
        "🧩 Тест уровня владения письменной речью\n\n"
        "Этот короткий тест поможет определить ваш текущий уровень и подобрать подходящие материалы курса.\n\n"
        "Вопрос 1 из 5\n\n"
        "«Зимой лес кажется спящим, но на самом деле жизнь в нем не замирает».\n\n"
        "Что здесь самое главное?",
        reply_markup=q1_kb
    )

@test_router.message(TestStates.question1, F.text.in_(["1️⃣ Зимой лес спит", "2️⃣ Жизнь в лесу продолжается", "3️⃣ Лес красивый"]))
async def question1_handler(message: Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await state.set_state(TestStates.question2)

    await message.answer(
        "Вопрос 2 из 5\n\n"
        "Как вам проще — устно рассказывать или письменно писать?",
        reply_markup=q2_kb
    )

@test_router.message(TestStates.question2, F.text.in_(["1️⃣ Устно", "2️⃣ Письменно", "3️⃣ Одинаково"]))
async def question2_handler(message: Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await state.set_state(TestStates.question3)

    await message.answer(
        "Вопрос 3 из 5\n\n"
        "Выберите лишнее слово:\nСочинение, Пересказ, Квадрат",
        reply_markup=q3_kb
    )

@test_router.message(TestStates.question3, F.text.in_(["Сочинение", "Пересказ", "Квадрат"]))
async def question3_handler(message: Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await state.set_state(TestStates.question4)

    await message.answer(
        "Вопрос 4 из 5\n\n"
        "Что труднее всего в сочинении?",
        reply_markup=q4_kb
    )

@test_router.message(TestStates.question4, F.text.in_(["1️⃣ Начать", "2️⃣ Продолжить (основная часть)", "3️⃣ Закончить"]))
async def question4_handler(message: Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await state.set_state(TestStates.question5)

    await message.answer(
        "Вопрос 5 из 5\n\n"
        "Напишите одним предложением, что вам было интересно на этой неделе ✍️\n\n"
        "Просто отправьте ваш ответ следующим сообщением:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    )

@test_router.message(TestStates.question5)
async def finish_test(message: Message, state: FSMContext):
    from bot import add_user_to_db
    await add_user_to_db(message.from_user)

    await state.update_data(q5=message.text)
    data = await state.get_data()

    # --- Логика определения уровня ---
    level = "Новичок"
    if data["q1"] == "2️⃣ Жизнь в лесу продолжается" and data["q3"] == "Квадрат":
        if data["q4"] == "3️⃣ Закончить":
            level = "Продвинутый"
        else:
            level = "Уверенный"

    # --- Рекомендации ---
    if level == "Новичок":
        rec = ("🌱 Вы умеете рассказывать устно, но письменно пока трудно начать. "
               "На курсе мы будем шаг за шагом тренировать, как превращать мысли в текст.\n\n"
               "💡 Совет до курса: ✍️ Записывайте каждый день одно предложение о своём дне.")
        emoji = "🌱"
    elif level == "Уверенный":
        rec = ("🌿 У вас уже получается писать, но иногда путаетесь в структуре. "
               "Мы научимся быстро видеть план текста и строить вступление и заключение.\n\n"
               "💡 Совет до курса: 📝 попробуйте к любому тексту составить план из 3 ключевых слов.")
        emoji = "🌿"
    else:
        rec = ("🌳 Вы легко выражаете мысли, теперь важно сделать их красивыми и выразительными. "
               "На курсе мы освоим стилистические техники и «украшения текста».\n\n"
               "💡 Совет до курса: 🎨 попробуйте использовать метафору или сравнение в каждом новом тексте.")
        emoji = "🌳"

    # Логируем результаты теста
    await log_test_result_to_db(message.from_user, data, level)

    result_text = f"""🎉 Тест завершён!

{emoji} Ваш уровень: **{level}**

{rec}

📚 Курс "Излагай ясно" поможет вам развить навыки письменной речи независимо от текущего уровня!

Хотите узнать больше о курсе? Выберите интересующий раздел в меню."""

    await message.answer(result_text, reply_markup=get_main_keyboard_with_test(), parse_mode="Markdown")
    await state.clear()

# Обработчик для неправильных ответов в тестах
@test_router.message(TestStates.question1)
@test_router.message(TestStates.question2)
@test_router.message(TestStates.question3)
@test_router.message(TestStates.question4)
async def invalid_test_answer(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == TestStates.question1:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов:", reply_markup=q1_kb)
    elif current_state == TestStates.question2:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов:", reply_markup=q2_kb)
    elif current_state == TestStates.question3:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов:", reply_markup=q3_kb)
    elif current_state == TestStates.question4:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов:", reply_markup=q4_kb)