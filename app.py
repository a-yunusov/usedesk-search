"""
Основной файл приложения для поиска тикетов Usedesk
Версия: 3.0 (модульная архитектура)
"""

from flask import Flask, render_template, request, jsonify
import logging
import os
from logging.handlers import RotatingFileHandler

# Импортируем наши модули
import config
import api_client
import utils

# Создаем директорию для логов
os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

# Настраиваем логирование
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=10*1024*1024,
            backupCount=10,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Создаем приложение Flask
app = Flask(__name__)
app.secret_key = config.SECRET_KEY


def enrich_ticket_data(ticket, users_dict):
    """
    Обогащает данные тикета дополнительной информацией.
    """
    # Получаем имя специалиста
    assignee_id = ticket.get('assignee_id')
    ticket['assignee_name'] = users_dict.get(assignee_id, 'Не назначен') if assignee_id else 'Не назначен'
    
    # Форматируем статус (получаем текст и CSS класс)
    status = ticket.get('status')
    status_text, status_class = utils.format_ticket_status(status)
    ticket['status_text'] = status_text
    ticket['status_class'] = status_class  # Сохраняем CSS класс
    
    # Форматируем дату создания
    created_at = ticket.get('created_at')
    ticket['created_at_formatted'] = utils.format_datetime(created_at)
    
    # Получаем информацию о клиенте
    ticket['client_info'] = utils.get_client_info(ticket)
    
    return ticket


def search_tickets(query, page=1):
    """
    Выполняет поиск тикетов с обогащением данных.
    
    Аргументы:
        query (str): Поисковый запрос
        page (int): Номер страницы
    
    Возвращает:
        tuple: (список тикетов, общее количество, общее количество страниц)
    """
    # Получаем тикеты из API
    tickets = api_client.search_tickets_api(query)
    
    # Получаем информацию о специалистах
    users_dict = api_client.get_users()
    
    # Обогащаем данные каждого тикета
    for ticket in tickets:
        enrich_ticket_data(ticket, users_dict)
    
    # Сортируем по дате (от новых к старым)
    tickets = utils.sort_tickets_by_date(tickets)
    
    # Применяем пагинацию
    paginated_tickets, total_tickets, total_pages = utils.paginate_tickets(
        tickets, 
        page, 
        config.TICKETS_PER_PAGE
    )
    
    logger.debug(f"Пагинация: страница {page} из {total_pages}, показано {len(paginated_tickets)} тикетов")
    
    return paginated_tickets, total_tickets, total_pages


@app.route('/')
def index():
    """Главная страница приложения"""
    logger.debug("Открыта главная страница")
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Эндпоинт для обработки поисковых запросов"""
    try:
        data = request.get_json()
        
        query = data.get('query', '').strip()
        page = int(data.get('page', 1))
        
        logger.info(f"Получен поисковый запрос: '{query}', страница: {page}")
        
        if not query:
            logger.warning("Получен пустой поисковый запрос")
            return jsonify({
                'error': 'Пожалуйста, введите поисковый запрос',
                'tickets': [],
                'total': 0,
                'page': 1,
                'total_pages': 0
            }), 400
        
        # Выполняем поиск
        tickets, total, total_pages = search_tickets(query, page)
        
        logger.info(f"Поиск завершён: найдено {total} тикетов")
        
        return jsonify({
            'tickets': tickets,
            'total': total,
            'page': page,
            'total_pages': total_pages
        })
    
    except TimeoutError as e:
        logger.error(f"Таймаут при поиске: {e}")
        return jsonify({
            'error': str(e),
            'tickets': [],
            'total': 0,
            'page': 1,
            'total_pages': 0
        }), 408
    
    except ConnectionError as e:
        logger.error(f"Ошибка подключения: {e}")
        return jsonify({
            'error': str(e),
            'tickets': [],
            'total': 0,
            'page': 1,
            'total_pages': 0
        }), 503
    
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        return jsonify({
            'error': str(e),
            'tickets': [],
            'total': 0,
            'page': 1,
            'total_pages': 0
        }), 500


if __name__ == '__main__':
    """Точка входа в приложение"""
    logger.info("=" * 60)
    logger.info("ЗАПУСК ПРИЛОЖЕНИЯ ПОИСКА ТИКЕТОВ USEDESK")
    logger.info(f"API URL: {config.BASE_URL}")
    logger.info(f"Таймаут API: {config.API_TIMEOUT} секунд")
    logger.info(f"Лог файл: {config.LOG_FILE}")
    logger.info(f"Сервер: http://{config.HOST}:{config.PORT}")
    logger.info(f"Debug режим: {config.DEBUG}")
    logger.info("=" * 60)
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)