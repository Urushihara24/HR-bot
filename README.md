<div align="center">

# 🤖 HR Telegram Bot

### Интеллектуальный Telegram-бот для автоматизации подбора персонала

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Автоматизируйте процесс подбора персонала с помощью умного чат-бота*

[Возможности](#-возможности) • [Установка](#-установка) • [Использование](#-использование) • [Технологии](#-технологии)

</div>

---

## 📋 Обзор проекта

**HR-bot** — это мощный и удобный инструмент для рекрутеров и соискателей, который автоматизирует самый трудоемкий этап — сбор и обработку анкет кандидатов. 

Бот ведет диалог с пользователем в Telegram, собирает информацию, валидирует данные и сохраняет результаты в Excel-файл для дальнейшей работы.

> 💡 **Проект демонстрирует опыт разработки современных чат-ботов с многошаговыми сценариями, сохранением состояния диалога и удобным интерфейсом на основе python-telegram-bot.**

---

## ✨ Возможности

<table>
<tr>
<td width="50%">

### 👤 Для кандидатов
- ✅ Автоматический сбор данных (ФИО, возраст, опыт, город, телефон)
- ✅ Валидация введенных данных
- ✅ Интерактивное меню вакансий
- ✅ Подробное описание каждой вакансии
- ✅ Быстрая подача заявки

</td>
<td width="50%">

### 👨‍💼 Для рекрутеров
- ✅ Администраторская панель
- ✅ Просмотр всех анкет в реальном времени
- ✅ Управление заявками (удаление, редактирование)
- ✅ Рассылка уведомлений кандидатам
- ✅ Экспорт данных в Excel

</td>
</tr>
</table>

### 🔧 Технические особенности

- **Многошаговый диалог** с сохранением состояния (FSM)
- **PicklePersistence** для запоминания контекста между запусками
- **Валидация данных** на каждом этапе
- **Гибкая система меню** с inline-клавиатурами
- **Автоматическое сохранение** в Excel (pandas + openpyxl)
- **Переменные окружения** для безопасного хранения токенов

---

## 🛠️ Технологии

<div align="center">

![Python](https://img.shields.io/badge/-Python_3.10+-3776AB?style=flat&logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/-python--telegram--bot-2CA5E0?style=flat&logo=telegram&logoColor=white)
![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat&logo=pandas&logoColor=white)
![OpenPyXL](https://img.shields.io/badge/-OpenPyXL-217346?style=flat&logo=microsoft-excel&logoColor=white)
![dotenv](https://img.shields.io/badge/-python--dotenv-ECD53F?style=flat&logo=python&logoColor=black)

</div>

### Основные библиотеки:

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| `python-telegram-bot` | 20.0+ | Работа с Telegram Bot API |
| `pandas` | 2.0+ | Обработка и сохранение данных |
| `openpyxl` | 3.1+ | Работа с Excel-файлами |
| `python-dotenv` | 1.0+ | Управление переменными окружения |

---

## 📦 Установка

### Требования:
- Python 3.10 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Шаг 1: Клонирование репозитория


Как использовать
Запустите бота в Telegram командой /start

Следуйте инструкциям для заполнения анкеты или просмотра вакансий

Администраторы могут использовать команды для управления заявками

