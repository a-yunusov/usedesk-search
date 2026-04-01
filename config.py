"""
Конфигурационный файл приложения
Все настраиваемые параметры вынесены сюда
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


# === API Usedesk ===
API_TOKEN = os.getenv('USEDESK_API_TOKEN', 'Сюда необходимо ввести API токен')
BASE_URL = os.getenv('USEDESK_BASE_URL', 'https://api.usedesk.ru')

# === Пагинация ===
TICKETS_PER_PAGE = int(os.getenv('TICKETS_PER_PAGE', '10'))

# === Таймауты ===
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))

# === Логирование ===
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# === Flask ===
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# === Сервер ===
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))