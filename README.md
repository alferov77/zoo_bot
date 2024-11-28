MZooQuizBot

# ОПИСАНИЕ

MZooQuizBot — это Telegram-бот, разработанный для проведения увлекательных викторин о Московском зоопарке. Пользователи могут пройти серию вопросов, узнать своё тотемное животное, оставить отзывы и связаться с сотрудниками зоопарка для получения дополнительной информации.

# ОСНОВНЫЕ ВОЗМОЖНОСТИ 

Викторина: Ответьте на 10 вопросов и узнайте, какое животное является вашим тотемом.
Обратная связь: Оставьте отзыв о работе бота или предложите свои идеи для улучшения.
Связаться с нами: Отправьте сообщение сотрудникам зоопарка для получения помощи или дополнительной информации.
Поделиться результатом: Делитесь своими результатами викторины в социальных сетях.
Конфиденциальность и безопасность: Бот соблюдает правила конфиденциальности данных и защищает информацию пользователей.
Начало работы

# ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ 
Python 3.7+: Убедитесь, что Python установлен на вашем компьютере. Скачайте его с официального сайта.
Telegram-аккаунт: Для взаимодействия с ботом.
Бот-токен от BotFather: Создайте бота и получите токен, следуя инструкции.

# УСТАНОВКА

1. Клонируйте репозиторий:
git clone https://github.com/alferov77/zoo_bot.git
cd zoo_bot

2. Создайте и активируйте виртуальное окружение:
На macOS/Linux:
python3 -m venv venv
source venv/bin/activate

3. На Windows:
python -m venv venv
venv\Scripts\activate

4. Установите зависимости:
pip install -r requirements.txt

5. Настройте переменные окружения:
Создайте файл .env в корневой папке проекта.

6. Добавьте в него ваш бот-токен:
BOT_TOKEN=your_bot_token_here

Важно: Файл .env уже добавлен в .gitignore, поэтому он не попадет в репозиторий и останется конфиденциальным.
Инициализируйте базу данных:
База данных feedback.db будет автоматически создана при первом запуске бота.

# ЗАПУСК БОТА
Убедитесь, что виртуальное окружение активировано, и выполните команду:
python3 bot.py

Если всё настроено правильно, бот начнёт работать и будет готов к взаимодействию.

# ИСПОЛЬЗОВАНИЕ

1. Начало викторины:
Отправьте команду /start вашему боту. Он проведёт вас через серию вопросов.
2. Ответы на вопросы:
Ответьте на каждый вопрос, выбирая один из предложенных вариантов.
3. Получение результата:
После завершения викторины бот отправит вам изображение вашего тотемного животного, ссылки для шаринга и информацию о программе опеки.
4. Оставить отзыв:
Нажмите кнопку "Оставить отзыв" и отправьте свой отзыв. Ваш отзыв будет сохранён в базе данных и доступен сотрудникам зоопарка.
5. Связаться с нами:
Нажмите кнопку "Связаться с нами", опишите вашу проблему или вопрос. Ваше сообщение будет переслано сотрудникам зоопарка вместе с результатом викторины.
6. Пройти ещё раз:
Нажмите кнопку "Пройти ещё раз" для начала новой викторины.

# ПРОЕКТНАЯ СТРУКТУРА

zoo_bot/
├── images/
│   ├── elephant.jpg
│   ├── lion.jpg
│   ├── meerkat.jpg
│   └── flamingo.jpg
├── feedback.db
├── bot.py
├── requirements.txt
├── .gitignore
└── .env

images/: Папка с изображениями животных.
feedback.db: База данных SQLite для хранения отзывов пользователей.
bot.py: Основной скрипт бота.
requirements.txt: Список зависимостей проекта.
.gitignore: Файл для игнорирования чувствительных данных.
.env: Файл с переменными окружения (не добавляется в репозиторий).

# БЕЗОПАСНОСТЬ И КОНФИДЕНЦИАЛЬНОСТЬ

Хранение токена: Токен бота хранится в файле .env и не включается в систему контроля версий благодаря настройкам .gitignore.
Конфиденциальность данных: Бот собирает только необходимые данные (ответы на викторину, отзывы, сообщения) и хранит их в базе данных feedback.db.
Ограничение доступа: Убедитесь, что файл feedback.db имеет ограниченные права доступа, чтобы предотвратить несанкционированный доступ.
Актуализация зависимостей

Чтобы актуализировать файл requirements.txt, выполните следующие шаги:

Активируйте виртуальное окружение:
На macOS/Linux:
source venv/bin/activate

На Windows:
venv\Scripts\activate

Установите или обновите необходимые пакеты:
pip install пакет_1 пакет_2

Сгенерируйте обновлённый requirements.txt:
pip freeze > requirements.txt

# ЛИЦЕНЗИЯ

Этот проект лицензирован под MIT License.

# КОНТАКТЫ

Если у вас возникли вопросы или предложения, свяжитесь со мной по адресу email@example.com или через Telegram.
