import logging
import os
import re
from typing import Dict

# Устанавливаем зависимости:
# pip install python-telegram-bot[job-queue] --pre
# pip install pandas openpyxl python-dotenv
import pandas as pd
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    PicklePersistence,
)

# Включаем логирование

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения (для токена)
load_dotenv()

# Состояния для ConversationHandler
(
    MENU,
    ASK_EXPERIENCE,
    ASK_CITIZENSHIP,
    ASK_FIO,
    ASK_AGE,
    ASK_CITY,
    ASK_PHONE,
    CONFIRM_DATA,
    VACANCIES_LIST,
    VACANCY_DESCRIPTION,
    ADMIN_MENU,
    DELETE_ID,
    SEND_MESSAGE,
) = range(13)

# Админ-IDs (используем set для быстрой проверки)
ADMIN_IDS = {1481790360, 196597371}

# Путь к файлу Excel
EXCEL_FILE = "hr_responses.xlsx"

# --- Функции для работы с Excel ---

def init_excel():
    """Создает Excel-файл, если он не существует."""
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'ID пользователя', 'Опыт по категории Е', 'Гражданство', 'ФИО', 'Возраст', 'Город', 'Телефон'
        ])
        df.to_excel(EXCEL_FILE, index=False)
        logger.info(f"Файл {EXCEL_FILE} создан.")

def save_to_excel(user_id: int, data: Dict):
    """Сохраняет новую строку с данными пользователя в Excel."""
    try:
        df = pd.read_excel(EXCEL_FILE)
        new_row = {
            'ID пользователя': user_id,
            'Опыт по категории Е': data.get('experience'),
            'Гражданство': data.get('citizenship'),
            'ФИО': data.get('fio'),
            'Возраст': data.get('age'),
            'Город': data.get('city'),
            'Телефон': data.get('phone')
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        logger.info(f"Данные пользователя {user_id} сохранены в Excel.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении в Excel: {e}")


# --- Основные обработчики ---

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет главное меню."""
    keyboard = [
        [KeyboardButton("📝 Заполнить анкету")],
        [KeyboardButton("💼 Список вакансий")],
    ]
    if update.effective_user.id in ADMIN_IDS:
        keyboard.append([KeyboardButton("🔐 Админка")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📋 Главное меню:", reply_markup=reply_markup)
    return MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start. Очищает старые данные и показывает меню."""
    context.user_data.clear()
    await main_menu(update, context)
    return MENU

# --- Логика главного меню ---

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в главном меню."""
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📝 Заполнить анкету":
        context.user_data.clear()
        keyboard = [
            [KeyboardButton("ДА"), KeyboardButton("НЕТ")],
            [KeyboardButton("⬅️ Назад в меню")]
        ]
        await update.message.reply_text(
            "❓ Есть ли у вас опыт работы водителем по категории Е?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_EXPERIENCE

    elif text == "💼 Список вакансий":
        keyboard = [
            [KeyboardButton("🚚 Водитель категории Е")],
            [KeyboardButton("📦 Водитель-экспедитор")],
            [KeyboardButton("⬅️ Назад в меню")]
        ]
        await update.message.reply_text("💼 Выберите вакансию:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return VACANCIES_LIST

    elif text == "🔐 Админка" and user_id in ADMIN_IDS:
        keyboard = [
            [KeyboardButton("📋 Просмотреть все анкеты")],
            [KeyboardButton("🗑 Удалить анкету")],
            [KeyboardButton("📢 Отправить всем сообщение")],
            [KeyboardButton("⬅️ Назад в меню")]
        ]
        await update.message.reply_text("🔐 Админ-панель:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ADMIN_MENU

    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MENU

# --- Логика заполнения анкеты ---

async def ask_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад в меню":
        context.user_data.clear()
        await main_menu(update, context)
        return MENU

    if text.upper() not in ["ДА", "НЕТ"]:
        await update.message.reply_text("❌ Пожалуйста, выберите 'ДА' или 'НЕТ'.")
        return ASK_EXPERIENCE

    context.user_data['experience'] = text.upper()
    keyboard = [
        [KeyboardButton("Россия"), KeyboardButton("СНГ"), KeyboardButton("Другое")],
        [KeyboardButton("⬅️ Назад")]
    ]
    await update.message.reply_text("🌍 Какое у вас гражданство?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ASK_CITIZENSHIP

async def ask_citizenship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [[KeyboardButton("ДА"), KeyboardButton("НЕТ")], [KeyboardButton("⬅️ Назад в меню")]]
        await update.message.reply_text(
            "❓ Есть ли у вас опыт работы водителем по категории Е?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_EXPERIENCE

    if text not in ["Россия", "СНГ", "Другое"]:
        await update.message.reply_text("❌ Выберите 'Россия', 'СНГ' или 'Другое'.")
        return ASK_CITIZENSHIP

    context.user_data['citizenship'] = text
    keyboard = [[KeyboardButton("⬅️ Назад")]]
    await update.message.reply_text(
        "👤 Введите ваше ФИО (например: Иванов Иван Иванович):",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ASK_FIO

async def ask_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [[KeyboardButton("Россия"), KeyboardButton("СНГ"), KeyboardButton("Другое")], [KeyboardButton("⬅️ Назад")]]
        await update.message.reply_text("🌍 Какое у вас гражданство?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ASK_CITIZENSHIP

    if len(text) < 5:
        await update.message.reply_text("❌ ФИО должно содержать хотя бы 5 символов.")
        return ASK_FIO

    context.user_data['fio'] = text
    keyboard = [[KeyboardButton("⬅️ Назад")]]
    await update.message.reply_text("🎂 Укажите ваш возраст (число):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ASK_AGE

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [[KeyboardButton("⬅️ Назад")]]
        await update.message.reply_text("👤 Введите ваше ФИО:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ASK_FIO

    if not text.isdigit() or not (16 <= int(text) <= 100):
        await update.message.reply_text("❌ Введите корректный возраст (от 16 до 100).")
        return ASK_AGE

    context.user_data['age'] = int(text)
    keyboard = [[KeyboardButton("⬅️ Назад")]]
    await update.message.reply_text("🏙 Укажите город проживания:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ASK_CITY

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [[KeyboardButton("⬅️ Назад")]]
        await update.message.reply_text("🎂 Укажите ваш возраст (число):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ASK_AGE

    if len(text) < 2:
        await update.message.reply_text("❌ Город должен содержать хотя бы 2 символа.")
        return ASK_CITY

    context.user_data['city'] = text
    keyboard = [[KeyboardButton("⬅️ Назад")]]
    await update.message.reply_text("📱 Укажите ваш номер телефона (например: +79991234567):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [[KeyboardButton("⬅️ Назад")]]
        await update.message.reply_text("🏙 Укажите город проживания:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ASK_CITY

    phone_pattern = r'^(\+7|8)\d{10}$'
    if not re.match(phone_pattern, text):
        await update.message.reply_text("❌ Неверный формат. Пример: +79991234567")
        return ASK_PHONE

    context.user_data['phone'] = text
    await show_confirmation(update, context)
    return CONFIRM_DATA

# --- Подтверждение и сохранение анкеты ---

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает пользователю введенные данные для подтверждения."""
    data = context.user_data
    message = (
        "📋 Пожалуйста, проверьте ваши данные:\n\n"
        f"🔸 Опыт по категории Е: {data['experience']}\n"
        f"🔸 Гражданство: {data['citizenship']}\n"
        f"🔸 ФИО: {data['fio']}\n"
        f"🔸 Возраст: {data['age']}\n"
        f"🔸 Город: {data['city']}\n"
        f"🔸 Телефон: {data['phone']}\n\n"
        "Всё верно?"
    )
    keyboard = [
        [KeyboardButton("✅ Отправить"), KeyboardButton("🔄 Заполнить заново")],
        [KeyboardButton("⬅️ Назад в меню")]
    ]
    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает подтверждение, сохраняет данные или начинает заново."""
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if text == "✅ Отправить":
        save_to_excel(user_id, context.user_data)
        await update.message.reply_text(
            "✅ Анкета успешно отправлена! Спасибо, мы с вами свяжемся.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        await main_menu(update, context)
        return MENU

    elif text == "🔄 Заполнить заново":
        context.user_data.clear()
        keyboard = [[KeyboardButton("ДА"), KeyboardButton("НЕТ")], [KeyboardButton("⬅️ Назад в меню")]]
        await update.message.reply_text(
            "🔄 Начнем заново.\n❓ Есть ли у вас опыт работы водителем по категории Е?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_EXPERIENCE

    elif text == "⬅️ Назад в меню":
        context.user_data.clear()
        await main_menu(update, context)
        return MENU

    else:
        await update.message.reply_text("❌ Пожалуйста, выберите один из вариантов: 'Отправить', 'Заполнить заново' или 'Назад в меню'.")
        return CONFIRM_DATA

# --- Логика раздела вакансий ---

async def handle_vacancy_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает описание выбранной вакансии."""
    text = update.message.text.strip()
    vacancy_info = {
        "🚚 Водитель категории Е": (
            "🚚 Водитель категории Е\n\n"
            "📌 Требования:\n"
            "- Опыт работы водителем категории Е\n"
            "- Готовность к дальним поездкам\n\n"
            "💼 Зарплата: от 120 000 руб.\n"
            "📍 Место работы: Москва, Санкт-Петербург"
        ),
        "📦 Водитель-экспедитор": (
            "📦 Водитель-экспедитор\n\n"
            "📌 Требования:\n"
            "- Опыт работы водителем\n"
            "- Ответственность\n\n"
            "💼 Зарплата: от 100 000 руб.\n"
            "📍 Место работы: Москва, регионы"
        )
    }

    if text == "⬅️ Назад в меню":
        await main_menu(update, context)
        return MENU

    if text in vacancy_info:
        description = vacancy_info[text] + "\n\n📩 Хотите откликнуться?"
        keyboard = [[KeyboardButton("✅ Откликнуться")], [KeyboardButton("⬅️ Назад")]]
        await update.message.reply_text(description, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return VACANCY_DESCRIPTION

    else:
        await update.message.reply_text("❌ Неизвестная вакансия. Выберите из списка.")
        return VACANCIES_LIST

async def handle_vacancy_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отклик на вакансию, перенаправляя на анкету."""
    text = update.message.text.strip()
    if text == "⬅️ Назад":
        keyboard = [
            [KeyboardButton("🚚 Водитель категории Е"), KeyboardButton("📦 Водитель-экспедитор")],
            [KeyboardButton("⬅️ Назад в меню")]
        ]
        await update.message.reply_text("💼 Выберите вакансию:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return VACANCIES_LIST

    elif text == "✅ Откликнуться":
        context.user_data.clear()
        keyboard = [[KeyboardButton("ДА"), KeyboardButton("НЕТ")], [KeyboardButton("⬅️ Назад в меню")]]
        await update.message.reply_text(
            "Отлично! Чтобы откликнуться, пожалуйста, заполните короткую анкету.\n\n"
            "❓ Есть ли у вас опыт работы водителем по категории Е?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_EXPERIENCE # Переход к заполнению анкеты

    else:
        await update.message.reply_text("❌ Выберите '✅ Откликнуться' или '⬅️ Назад'.")
        return VACANCY_DESCRIPTION

# --- Функции админ-панели ---

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды из админ-меню."""
    text = update.message.text.strip()
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🔒 Доступ запрещён.")
        return MENU

    if text == "⬅️ Назад в меню":
        await main_menu(update, context)
        return MENU

    elif text == "📋 Просмотреть все анкеты":
        await view_all_ankets(update, context)
        return ADMIN_MENU

    elif text == "🗑 Удалить анкету":
        await update.message.reply_text("Введите ID пользователя, анкету которого нужно удалить:")
        return DELETE_ID

    elif text == "📢 Отправить всем сообщение":
        await update.message.reply_text("📝 Напишите сообщение для рассылки всем, кто заполнил анкету:")
        return SEND_MESSAGE

    else:
        await update.message.reply_text("❌ Неизвестная команда. Выберите из меню.")
        return ADMIN_MENU


async def view_all_ankets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет админу список всех анкет из Excel файла."""
    if update.effective_user.id not in ADMIN_IDS:
        return MENU
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            await update.message.reply_text("📭 В базе данных пока нет ни одной анкеты.")
            return ADMIN_MENU

        for index, row in df.iterrows():
            anketa_text = (
                f"👤 Анкета #{index + 1}\n"
                f"ID: {row['ID пользователя']}\n"
                f"ФИО: {row['ФИО']}\n"
                f"Возраст: {row['Возраст']}\n"
                f"Город: {row['Город']}\n"
                f"Телефон: {row['Телефон']}\n"
                f"Гражданство: {row['Гражданство']}\n"
                f"Опыт: {row['Опыт по категории Е']}\n"
            )
            await update.message.reply_text(anketa_text)
    except FileNotFoundError:
        await update.message.reply_text(f"❌ Файл {EXCEL_FILE} не найден.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка при чтении анкет: {e}")
    return ADMIN_MENU


async def delete_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет анкету пользователя по ID."""
    if update.effective_user.id not in ADMIN_IDS:
        return MENU
    try:
        target_id = int(update.message.text.strip())
        df = pd.read_excel(EXCEL_FILE)
        initial_count = len(df)
        df = df[df['ID пользователя'] != target_id]

        if len(df) < initial_count:
            df.to_excel(EXCEL_FILE, index=False)
            await update.message.reply_text(f"✅ Анкета пользователя с ID {target_id} успешно удалена.")
        else:
            await update.message.reply_text(f"❌ Анкета пользователя с ID {target_id} не найдена.")
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID. Введите число.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при удалении: {e}")

    await main_menu(update, context) # Возвращаем в главное меню после действия
    return MENU


async def send_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполняет рассылку сообщения всем пользователям из базы."""
    if update.effective_user.id not in ADMIN_IDS:
        return MENU

    message_text = update.message.text
    bot = context.bot
    try:
        df = pd.read_excel(EXCEL_FILE)
        unique_user_ids = df['ID пользователя'].unique()
        sent_count, error_count = 0, 0

        for user_id in unique_user_ids:
            try:
                await bot.send_message(chat_id=int(user_id), text=message_text)
                sent_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

        await update.message.reply_text(
            f"📬 Рассылка завершена:\n"
            f"✅ Успешно отправлено: {sent_count}\n"
            f"❌ Ошибок: {error_count}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при выполнении рассылки: {e}")

    await main_menu(update, context) # Возвращаем в главное меню после действия
    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет текущую операцию и возвращает в главное меню."""
    context.user_data.clear()
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    await main_menu(update, context)
    return MENU

# --- Сборка и запуск бота ---

def main():
    """Главная функция для запуска бота."""
    init_excel()

    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("Необходимо установить TELEGRAM_TOKEN в переменных окружения (в файле .env).")

    # Создаем persistence для сохранения данных между перезапусками
    persistence = PicklePersistence(filepath="bot_data")

    application = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            # Состояния анкеты
            ASK_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_experience)],
            ASK_CITIZENSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_citizenship)],
            ASK_FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_fio)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            CONFIRM_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_data)],
            # Состояния вакансий
            VACANCIES_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vacancy_selection)],
            VACANCY_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vacancy_response)],
            # Состояния админки
            ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_menu)],
            DELETE_ID: [MessageHandler(filters.TEXT, delete_id_handler)],
            SEND_MESSAGE: [MessageHandler(filters.TEXT, send_message_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        persistent=True,
        name="main_conversation",
    )

    application.add_handler(conv_handler)

    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()

