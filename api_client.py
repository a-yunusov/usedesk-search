"""
Модуль для работы с API Usedesk
Содержит все функции для взаимодействия с API
"""

import requests
import logging
import config

logger = logging.getLogger(__name__)

# Кэш для хранения списка пользователей
users_cache = None
cache_timestamp = None
CACHE_DURATION = 300  # Кэш живёт 5 минут


def get_users():
    """
    Получает список всех пользователей (специалистов) из Usedesk API.
    Использует кэширование для уменьшения количества запросов к API.
    
    Возвращает:
        dict: Словарь вида {user_id: user_name}
    """
    global users_cache, cache_timestamp
    from datetime import datetime, timedelta
    
    # Проверяем, есть ли актуальный кэш
    if users_cache is not None and cache_timestamp is not None:
        if datetime.now() - cache_timestamp < timedelta(seconds=CACHE_DURATION):
            logger.debug("Используем кэшированный список пользователей")
            return users_cache
    
    # Формируем полный URL для запроса списка пользователей
    url = f"{config.BASE_URL}/users"
    
    # Параметры запроса
    params = {
        "api_token": config.API_TOKEN
    }
    
    try:
        logger.info(f"Запрос списка пользователей к API: {url}")
        
        # Отправляем GET запрос к API Usedesk
        response = requests.get(url, params=params, timeout=config.API_TIMEOUT)
        response.raise_for_status()
        
        # Получаем JSON ответ
        users_data = response.json()
        
        # Создаем словарь для быстрого поиска имени по ID
        users_dict = {}
        
        for user in users_data:
            user_name = user.get('name', 'Неизвестный специалист')
            user_id = user.get('id')
            
            if user_id:
                users_dict[user_id] = user_name
        
        # Сохраняем в кэш
        users_cache = users_dict
        cache_timestamp = datetime.now()
        
        logger.info(f"Успешно получено {len(users_dict)} пользователей из API")
        return users_dict
    
    except requests.exceptions.Timeout as e:
        error_msg = f"Таймаут при получении списка пользователей: {e}"
        logger.error(error_msg)
        return {}
    
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Ошибка подключения при получении списка пользователей: {e}"
        logger.error(error_msg)
        return {}
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка при получении списка пользователей: {e.response.status_code}"
        logger.error(error_msg)
        return {}
    
    except Exception as e:
        logger.exception(f"Критическая ошибка при получении списка пользователей: {e}")
        return {}


def search_tickets_api(query):
    """
    Выполняет поиск тикетов в Usedesk API по заданному запросу.
    
    Аргументы:
        query (str): Текст для поиска
    
    Возвращает:
        list: Список тикетов или пустой список при ошибке
    """
    url = f"{config.BASE_URL}/tickets"
    
    params = {
        "api_token": config.API_TOKEN,
        "query": query
    }
    
    try:
        logger.info(f"Поиск тикетов по запросу: '{query}'")
        
        response = requests.get(url, params=params, timeout=config.API_TIMEOUT)
        response.raise_for_status()
        
        tickets = response.json()
        
        logger.info(f"Найдено {len(tickets)} тикетов по запросу: '{query}'")
        return tickets
    
    except requests.exceptions.Timeout as e:
        error_msg = f"Таймаут при поиске тикетов (запрос: '{query}'): {e}"
        logger.error(error_msg)
        raise TimeoutError(f"Запрос к API занял более {config.API_TIMEOUT} секунд. Попробуйте позже.")
    
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Ошибка подключения при поиске тикетов (запрос: '{query}'): {e}"
        logger.error(error_msg)
        raise ConnectionError("Не удалось подключиться к серверу Usedesk.")
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = f"HTTP ошибка {status_code} при поиске тикетов (запрос: '{query}')"
        logger.error(error_msg)
        
        if status_code == 401:
            raise Exception("Ошибка авторизации. Проверьте API токен.")
        elif status_code == 429:
            raise Exception("Слишком много запросов. Подождите немного и повторите попытку.")
        else:
            raise Exception(f"Ошибка сервера Usedesk: {status_code}")
    
    except Exception as e:
        logger.exception(f"Ошибка при поиске тикетов (запрос: '{query}'): {e}")
        raise