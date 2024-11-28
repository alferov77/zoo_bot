import logging
import urllib.parse
import sqlite3  # Импортируем sqlite3
import os
from dotenv import load_dotenv
from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')  # Получаем токен из .env

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные и константы
BOT_USERNAME = 'MZooQuizBot'
BOT_LINK = f'https://t.me/{BOT_USERNAME}'

STAFF_CHAT_ID = 1846976346

questions = [
    "1️⃣ Как вы предпочитаете проводить свободное время?",
    "2️⃣ Какая ваша любимая еда?",
    "3️⃣ Какое место для жизни вам больше нравится?",
    "4️⃣ Как бы вас описали друзья?",
    "5️⃣ Что вам больше всего нравится делать на выходных?",
    "6️⃣ Какой ваш любимый сезон?",
    "7️⃣ Как вы относитесь к риску?",
    "8️⃣ Какой стиль музыки вам нравится?",
    "9️⃣ Что для вас важнее всего?",
    "🔟 Как вы справляетесь со стрессом?"
]

options = [
    ["A) Активно, занимаясь спортом", "B) Читая книги и изучая что-то новое", "C) Общаясь с друзьями", "D) Отдыхая на природе"],
    ["A) Фрукты и овощи", "B) Мясо", "C) Рыба и морепродукты", "D) Орехи и семена"],
    ["A) Лес", "B) Горы", "C) Саванна", "D) Пустыня"],
    ["A) Мудрый и спокойный", "B) Энергичный и смелый", "C) Общительный и дружелюбный", "D) Независимый и задумчивый"],
    ["A) Путешествовать", "B) Посещать музеи и выставки", "C) Встречаться с друзьями", "D) Заниматься хобби в одиночестве"],
    ["A) Весна", "B) Лето", "C) Осень", "D) Зима"],
    ["A) Люблю рисковать", "B) Предпочитаю стабильность", "C) Зависит от ситуации", "D) Избегаю риска"],
    ["A) Классическая", "B) Рок", "C) Поп-музыка", "D) Джаз"],
    ["A) Семья", "B) Карьера", "C) Друзья", "D) Саморазвитие"],
    ["A) Занимаюсь спортом", "B) Разговариваю с близкими", "C) Медитирую", "D) Слушаю музыку"]
]

animals = {
    'A': 'Слон',
    'B': 'Лев',
    'C': 'Сурикат',
    'D': 'Фламинго'
}

animal_links = {
    'Слон': 'https://moscowzoo.ru/animals/kinds/afrikanskiy_slon',
    'Лев': 'https://moscowzoo.ru/animals/kinds/indiyskiy_лев',
    'Сурикат': 'https://moscowzoo.ru/animals/kinds/surikat',
    'Фламинго': 'https://moscowzoo.ru/animals/kinds/rozovyy_flamingo'
}

animal_images = {
    'Слон': 'images/elephant.jpg',
    'Лев': 'images/lion.jpg',
    'Сурикат': 'images/meerkat.jpg',
    'Фламинго': 'images/flamingo.jpg'
}

# Определяем состояния для ConversationHandler
FEEDBACK = 1
CONTACT = 2

def init_db():
    try:
        conn = sqlite3.connect('feedback.db')  # Создаём или подключаемся к базе данных
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT,
                user_id INTEGER,
                feedback_text TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

def generate_twitter_share(animal, link):
    share_text = f"Я прошёл викторину Московского зоопарка, и моё тотемное животное - {animal}! Узнать больше: {link}"
    return f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"

def generate_facebook_share(animal, link):
    share_url = BOT_LINK
    return f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(share_url)}"

async def send_final_buttons(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    final_buttons = [
        [
            InlineKeyboardButton("Пройти еще раз", callback_data='restart'),
            InlineKeyboardButton("Оставить отзыв", callback_data='feedback'),
            InlineKeyboardButton("Связаться с нами", callback_data='contact')
        ]
    ]
    final_reply_markup = InlineKeyboardMarkup(final_buttons)
    
    try:
        final_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Выберите дальнейшее действие:",
            reply_markup=final_reply_markup
        )
        context.user_data['final_message_id'] = final_message.message_id
        logger.debug(f"Финальное сообщение отправлено с message_id={final_message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке финального сообщения: {e}")
        await context.bot.send_message(chat_id=chat_id, text="К сожалению, произошла ошибка.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 🐾\n"
        "Добро пожаловать в викторину Московского зоопарка!\n\n"
        "Мы собираем ваши ответы на вопросы викторины и, при необходимости, отзывы и контактные сообщения для улучшения нашего сервиса.\n\n"
        "Давайте узнаем, какое у вас тотемное животное. Ответьте на несколько вопросов."
    )
    context.user_data['answers'] = []
    context.user_data['current_question'] = 0
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_num = context.user_data['current_question']
    if q_num < len(questions):
        question = questions[q_num]
        options_list = options[q_num]
        buttons = [
            [InlineKeyboardButton(option, callback_data=option[0].upper())] for option in options_list
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        if q_num == 0 and update.message:
            await update.message.reply_text(question, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(question, reply_markup=reply_markup)
    else:
        await show_result(update, context)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answer = query.data
    context.user_data['answers'].append(answer)
    context.user_data['current_question'] += 1
    await send_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Определение результата
    answers = context.user_data['answers']
    count = Counter(answers)
    result = count.most_common(1)[0][0]  # Наиболее часто встречающийся ответ
    animal = animals.get(result, 'Неизвестное животное')
    link = animal_links.get(animal, 'https://moscowzoo.ru/')
    image_path = animal_images.get(animal)

    chat_id = update.effective_chat.id

    # Сохранение результата викторины
    context.user_data['animal'] = animal
    context.user_data['animal_link'] = link

    # Отправка изображения и сохранение message_id
    try:
        with open(image_path, 'rb') as photo:
            photo_message = await context.bot.send_photo(chat_id=chat_id, photo=photo)
            context.user_data['photo_message_id'] = photo_message.message_id
            logger.debug(f"Фото отправлено с message_id={photo_message.message_id} в chat_id={photo_message.chat.id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await context.bot.send_message(chat_id=chat_id, text="К сожалению, не удалось отправить изображение.")

    # Сообщение с результатом и кнопкой "Узнать об этом животном"
    animal_message_text = f"Ваше животное - {animal}! 🎉"
    animal_button = InlineKeyboardButton("Узнать об этом животном", url=link)
    animal_reply_markup = InlineKeyboardMarkup([[animal_button]])

    try:
        animal_message = await context.bot.send_message(
            chat_id=chat_id,
            text=animal_message_text,
            reply_markup=animal_reply_markup
        )
        context.user_data['animal_message_id'] = animal_message.message_id
        logger.debug(f"Сообщение с животным отправлено с message_id={animal_message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения с животным: {e}")
        await context.bot.send_message(chat_id=chat_id, text="К сожалению, произошла ошибка при отправке результата.")

    # Генерация ссылок для шаринга
    twitter_share_url = generate_twitter_share(animal, link)
    facebook_share_url = generate_facebook_share(animal, link)
    instagram_share_url = "https://www.instagram.com/"  # Instagram не поддерживает прямой шаринг через URL

    # Кнопки для шаринга
    share_buttons = [
        InlineKeyboardButton("Facebook", url=facebook_share_url),
        InlineKeyboardButton("Twitter (X)", url=twitter_share_url),
        InlineKeyboardButton("Instagram", url=instagram_share_url)
    ]
    # Располагаем кнопки в столбик, если не помещаются в строку
    share_reply_markup = InlineKeyboardMarkup([share_buttons])

    # Отправка сообщения с кнопками для шаринга
    try:
        share_message = await context.bot.send_message(
            chat_id=chat_id,
            text="Поделитесь своим результатом:",
            reply_markup=share_reply_markup
        )
        context.user_data['share_message_id'] = share_message.message_id
        logger.debug(f"Сообщение для шаринга отправлено с message_id={share_message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения для шаринга: {e}")
        await context.bot.send_message(chat_id=chat_id, text="К сожалению, произошла ошибка при отправке кнопок для шаринга.")

    # Сообщение с информацией о программе опеки и кнопкой
    program_message_text = (
        "Московский зоопарк приглашает вас принять участие в программе 'Возьми животное под опеку' ('Клуб друзей').\n"
        "Вы можете стать опекуном и помочь в сохранении биоразнообразия планеты."
    )
    program_button = InlineKeyboardButton(
        "Хотите узнать об этой программе больше?",
        url="https://moscowzoo.ru/about/guardianship"
    )
    program_reply_markup = InlineKeyboardMarkup([[program_button]])

    try:
        program_message = await context.bot.send_message(
            chat_id=chat_id,
            text=program_message_text,
            reply_markup=program_reply_markup
        )
        context.user_data['program_message_id'] = program_message.message_id
        logger.debug(f"Сообщение с программой отправлено с message_id={program_message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения с программой: {e}")
        await context.bot.send_message(chat_id=chat_id, text="К сожалению, произошла ошибка при отправке информации о программе.")

    # Отправка финальных кнопок
    await send_final_buttons(chat_id, context)

    # Сохраняем все message_id для последующего удаления (исключая final_message_id)
    context.user_data['result_message_ids'] = [
        animal_message.message_id,
        share_message.message_id,
        program_message.message_id
    ]


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Удаление предыдущего изображения
    if 'photo_message_id' in context.user_data:
        photo_message_id = context.user_data['photo_message_id']
        logger.debug(f"Попытка удалить фото с message_id={photo_message_id}")
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=photo_message_id)
        except Exception as e:
            logger.error(f"Ошибка при удалении фото: {e}")
        else:
            del context.user_data['photo_message_id']

    # Удаление сообщений с результатом (исключая финальное сообщение)
    if 'result_message_ids' in context.user_data:
        for message_id in context.user_data['result_message_ids']:
            logger.debug(f"Попытка удалить сообщение с message_id={message_id}")
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения с message_id={message_id}: {e}")
        del context.user_data['result_message_ids']

    # Сброс данных пользователя и начало новой викторины
    context.user_data['answers'] = []
    context.user_data['current_question'] = 0
    await send_question(update, context)


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, отправьте ваш отзыв одним сообщением."
    )
    return FEEDBACK  # Переходим в состояние ожидания отзыва

async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_text = update.message.text
    user = update.message.from_user
    username = user.username if user.username else user.first_name
    timestamp = update.message.date.strftime('%Y-%m-%d %H:%M:%S')
    
    # Сохранение отзыва в базу данных
    try:
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (timestamp, username, user_id, feedback_text)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, username, user.id, feedback_text))
        conn.commit()
        conn.close()
        logger.debug(f"Отзыв от {username} (ID: {user.id}) сохранён.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении отзыва: {e}")
        await update.message.reply_text("К сожалению, произошла ошибка при сохранении вашего отзыва.")
        return ConversationHandler.END
    
    await update.message.reply_text("Спасибо за ваш отзыв!")
    
    # Отправка финальных кнопок
    await send_final_buttons(update.effective_chat.id, context)
    
    return ConversationHandler.END  # Завершаем разговор


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, опишите вашу проблему или вопрос, и мы свяжемся с вами."
    )
    return CONTACT  # Переходим в состояние ожидания сообщения от пользователя

async def receive_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.message.from_user
    animal = context.user_data.get('animal', 'Неизвестное животное')
    animal_link = context.user_data.get('animal_link', 'https://moscowzoo.ru/')
    
    # Формирование сообщения для сотрудника
    staff_message = (
        f"📢 **Новый запрос от пользователя:**\n\n"
        f"**Пользователь:** {user.first_name} (@{user.username})\n"
        f"**Тотемное животное:** {animal}\n"
        f"**Узнать об этом животном:** {animal_link}\n\n"
        f"**Сообщение пользователя:**\n{user_message}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=STAFF_CHAT_ID,
            text=staff_message,
            parse_mode='Markdown'
        )
        logger.debug(f"Сообщение от пользователя {user.id} отправлено сотруднику.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения сотруднику: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="К сожалению, произошла ошибка при отправке вашего сообщения.")
    
    await update.message.reply_text("Спасибо! Ваше сообщение было отправлено сотруднику. Мы свяжемся с вами в ближайшее время.")
    
    # Отправка финальных кнопок
    await send_final_buttons(update.effective_chat.id, context)
    
    return ConversationHandler.END  # Завершаем разговор


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Извините, я не понимаю эту команду. Пожалуйста, используйте кнопки ниже.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Инициализация базы данных
    init_db()
    
    # Обработчики команд
    application.add_handler(CommandHandler('start', start))
    
    # Обработчики callback'ов
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='^[ABCD]$'))
    application.add_handler(CallbackQueryHandler(restart, pattern='^restart$'))
    application.add_handler(CallbackQueryHandler(contact, pattern='^contact$'))
    
    # Обработчик для кнопки "Оставить отзыв" через ConversationHandler
    feedback_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(feedback, pattern='^feedback$')],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback)]
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(feedback_conv_handler)
    
    # Обработчик для кнопки "Связаться с нами" через отдельный ConversationHandler
    contact_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact, pattern='^contact$')],
        states={
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contact_message)]
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(contact_conv_handler)
    
    # Обработчик неизвестных сообщений
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()